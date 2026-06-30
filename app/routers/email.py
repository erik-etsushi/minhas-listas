import os
import random
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/api", tags=["email"])


def _verify_secret(x_secret_token: str = Header(default=None)):
    expected = os.environ.get("EMAIL_SECRET_TOKEN", "")
    if not expected or x_secret_token != expected:
        raise HTTPException(status_code=403, detail="Forbidden")


def _pick_random_filme(db: Session, lista_nome: str):
    lista = db.query(models.Lista).filter(models.Lista.nome == lista_nome).first()
    if not lista or not lista.filmes:
        return None
    return random.choice(lista.filmes)


def _pick_random_citacao(db: Session):
    citacoes = db.query(models.Citacao).all()
    return random.choice(citacoes) if citacoes else None


def _item_card_html(item, label, show_autor=False):
    if not item:
        return f"<h2>{label}</h2><p style='color:#888'>Nenhum item cadastrado ainda.</p>"
    img = (
        f'<img src="{item.poster_url}" alt="capa" style="width:90px;border-radius:4px;margin-right:12px;flex-shrink:0"/>'
        if getattr(item, "poster_url", "")
        else ""
    )
    autor_line = f"<br/>Autor: {item.autor}" if show_autor and getattr(item, "autor", "") else ""
    nota_line = f"<br/>Nota: {item.nota}/10" if getattr(item, "nota", None) is not None else ""
    coment = f"<br/><em style='color:#aaa'>{item.comentario}</em>" if getattr(item, "comentario", "") else ""
    return (
        f'<h2 style="color:#333;margin-bottom:8px">{label}</h2>'
        f'<div style="display:flex;margin-bottom:24px;">'
        f"{img}"
        f"<div><strong>{item.titulo}</strong> ({item.ano or '—'}){autor_line}{nota_line}{coment}</div>"
        f"</div>"
    )


def _citacao_card_html(c):
    if not c:
        return "<h2>Citação do dia</h2><p style='color:#888'>Nenhuma citação cadastrada ainda.</p>"
    attr = f"— {c.autor}" if c.autor else ""
    return (
        '<h2 style="color:#333;margin-bottom:8px">Citação do dia</h2>'
        '<blockquote style="border-left:3px solid #6366f1;margin:0 0 24px 0;padding:8px 16px;color:#444;font-style:italic;">'
        f'"{c.citacao}"'
        f'<footer style="margin-top:6px;font-size:13px;color:#777;font-style:normal">{attr}</footer>'
        "</blockquote>"
    )


def _build_html(livro, filme, citacao) -> str:
    return (
        '<html><body style="font-family:sans-serif;background:#f5f5f5;padding:20px;">'
        '<div style="max-width:600px;margin:auto;background:white;border-radius:8px;padding:24px;">'
        '<h1 style="color:#1a1a1a">Sua dose cultural diária</h1>'
        + _item_card_html(livro, "Livro do dia", show_autor=True)
        + _item_card_html(filme, "Filme do dia")
        + _citacao_card_html(citacao)
        + f'<p style="font-size:12px;color:#aaa;margin-top:16px;">Enviado em {date.today().strftime("%d/%m/%Y")}</p>'
        "</div></body></html>"
    )


def _build_plain(livro, filme, citacao) -> str:
    def fmt_filme(item, show_autor=False):
        if not item:
            return "  (nenhum item cadastrado)"
        autor = f"\n  Autor: {item.autor}" if show_autor and item.autor else ""
        nota = f"\n  Nota: {item.nota}/10" if item.nota is not None else ""
        coment = f"\n  {item.comentario}" if item.comentario else ""
        return f"  {item.titulo} ({item.ano or '—'}){autor}{nota}{coment}"

    def fmt_citacao(c):
        if not c:
            return "  (nenhuma citação cadastrada)"
        return f'  "{c.citacao}"\n  — {c.autor}' if c.autor else f'  "{c.citacao}"'

    return (
        f"LIVRO DO DIA\n{fmt_filme(livro, True)}\n\n"
        f"FILME DO DIA\n{fmt_filme(filme)}\n\n"
        f"CITAÇÃO DO DIA\n{fmt_citacao(citacao)}"
    )


def _send_email(livro, filme, citacao):
    gmail_user = os.environ["GMAIL_USER"]
    gmail_pass = os.environ["GMAIL_APP_PASSWORD"]
    email_to = os.environ["EMAIL_TO"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Listas do dia — {date.today().strftime('%d/%m/%Y')}"
    msg["From"] = gmail_user
    msg["To"] = email_to
    msg.attach(MIMEText(_build_plain(livro, filme, citacao), "plain"))
    msg.attach(MIMEText(_build_html(livro, filme, citacao), "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmail_user, gmail_pass)
        smtp.sendmail(gmail_user, email_to, msg.as_string())


@router.post("/send-daily-email", status_code=200)
def send_daily_email(
    _: None = Depends(_verify_secret),
    db: Session = Depends(get_db),
):
    if os.environ.get("EMAIL_ENABLED", "true").lower() == "false":
        return {"status": "disabled"}

    livro = _pick_random_filme(db, "Livros")
    filme = _pick_random_filme(db, "Filmes")
    citacao = _pick_random_citacao(db)

    try:
        _send_email(livro, filme, citacao)
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Env var ausente: {e}")
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=500, detail=f"Erro SMTP: {e}")

    return {
        "status": "sent",
        "livro": livro.titulo if livro else None,
        "filme": filme.titulo if filme else None,
        "citacao": citacao.citacao[:60] if citacao else None,
    }
