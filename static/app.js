function app() {
  return {
    tabs: {
      filmes:   { label: 'Filmes',   emoji: '🎬' },
      series:   { label: 'Séries',   emoji: '📺' },
      livros:   { label: 'Livros',   emoji: '📚' },
      citacoes: { label: 'Citações', emoji: '💬' },
    },
    tipo: 'filmes',
    listaIds: { filmes: null, series: null, livros: null },
    listas:   { filmes: null, series: null, livros: null },
    carregando: false,

    buscaAberta: false,
    termoBusca: '',
    resultadosBusca: [],
    buscando: false,
    _debounce: null,

    notasAbertas: false,
    itemNotas: null,
    formNotas: { nota: null, comentario: '' },

    citacoes: null,
    citacaoAberta: false,
    itemCitacao: null,
    formCitacao: { citacao: '', autor: '' },

    toast: { msg: '', tipo: 'ok' },
    _toastTimer: null,

    async init() {
      this.carregando = true;
      try {
        const [rListas, rCitacoes] = await Promise.all([
          fetch('/api/listas/'),
          fetch('/api/citacoes/'),
        ]);
        const todas = await rListas.json();
        const mapa = { 'Filmes': 'filmes', 'Séries': 'series', 'Livros': 'livros' };
        for (const l of todas) {
          const t = mapa[l.nome];
          if (t) this.listaIds[t] = l.id;
        }
        this.citacoes = await rCitacoes.json();
        await this._carregarLista(this.tipo);
      } catch {
        this.mostrarToast('Erro ao carregar dados.', 'erro');
      } finally {
        this.carregando = false;
      }
    },

    async _carregarLista(tipo) {
      const id = this.listaIds[tipo];
      if (!id) return;
      const r = await fetch(`/api/listas/${id}`);
      this.listas[tipo] = await r.json();
    },

    get itensAtivos() {
      if (this.tipo === 'citacoes') return this.citacoes || [];
      return this.listas[this.tipo]?.filmes || [];
    },

    get listaAtivaId() {
      return this.listaIds[this.tipo];
    },

    async trocarTipo(novoTipo) {
      if (this.tipo === novoTipo && !this.buscaAberta) return;
      this.fecharBusca();
      this.tipo = novoTipo;
      if (novoTipo !== 'citacoes' && !this.listas[novoTipo]) {
        this.carregando = true;
        try { await this._carregarLista(novoTipo); }
        finally { this.carregando = false; }
      }
    },

    abrirBusca() {
      if (this.tipo === 'citacoes') {
        this.abrirCitacao(null);
        return;
      }
      this.buscaAberta = true;
      this.termoBusca = '';
      this.resultadosBusca = [];
      this.$nextTick(() => this.$refs.searchInput?.focus());
    },

    fecharBusca() {
      this.buscaAberta = false;
      clearTimeout(this._debounce);
    },

    pesquisar() {
      clearTimeout(this._debounce);
      if (!this.termoBusca.trim()) {
        this.resultadosBusca = [];
        return;
      }
      this._debounce = setTimeout(async () => {
        this.buscando = true;
        try {
          const q = encodeURIComponent(this.termoBusca.trim());
          const r = await fetch(`/api/search/?q=${q}&tipo=${this.tipo}`);
          this.resultadosBusca = await r.json();
        } catch {
          this.mostrarToast('Erro na busca.', 'erro');
        } finally {
          this.buscando = false;
        }
      }, 450);
    },

    jaAdicionado(item) {
      return this.itensAtivos.some(
        f => f.titulo === item.titulo && f.ano === item.ano
      );
    },

    async adicionarDaBusca(item) {
      try {
        const r = await fetch(`/api/listas/${this.listaAtivaId}/filmes/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(item),
        });
        if (!r.ok) throw new Error();
        const novo = await r.json();
        this.listas[this.tipo].filmes.push(novo);
        this.mostrarToast(`"${item.titulo}" adicionado!`, 'ok');
      } catch {
        this.mostrarToast('Erro ao adicionar.', 'erro');
      }
    },

    async removerItem(item) {
      if (this.tipo === 'citacoes') {
        await this.removerCitacao(item);
        return;
      }
      if (!confirm(`Remover "${item.titulo}"?`)) return;
      try {
        const r = await fetch(`/api/listas/${this.listaAtivaId}/filmes/${item.id}`, { method: 'DELETE' });
        if (!r.ok) throw new Error();
        this.listas[this.tipo].filmes = this.listas[this.tipo].filmes.filter(f => f.id !== item.id);
      } catch {
        this.mostrarToast('Erro ao remover.', 'erro');
      }
    },

    abrirNotas(item) {
      if (this.tipo === 'citacoes') {
        this.abrirCitacao(item);
        return;
      }
      this.itemNotas = item;
      this.formNotas = { nota: item.nota ?? null, comentario: item.comentario || '' };
      this.notasAbertas = true;
    },

    fecharNotas() {
      this.notasAbertas = false;
      this.itemNotas = null;
    },

    async salvarNotas() {
      const item = this.itemNotas;
      try {
        const r = await fetch(`/api/listas/${this.listaAtivaId}/filmes/${item.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formNotas),
        });
        if (!r.ok) throw new Error();
        const atualizado = await r.json();
        Object.assign(item, atualizado);
        this.fecharNotas();
        this.mostrarToast('Notas salvas!', 'ok');
      } catch {
        this.mostrarToast('Erro ao salvar notas.', 'erro');
      }
    },

    abrirCitacao(item) {
      this.itemCitacao = item;
      this.formCitacao = item
        ? { citacao: item.citacao, autor: item.autor || '' }
        : { citacao: '', autor: '' };
      this.citacaoAberta = true;
    },

    fecharCitacao() {
      this.citacaoAberta = false;
      this.itemCitacao = null;
    },

    async salvarCitacao() {
      const isEdit = !!this.itemCitacao;
      const url    = isEdit ? `/api/citacoes/${this.itemCitacao.id}` : '/api/citacoes/';
      const method = isEdit ? 'PUT' : 'POST';
      try {
        const r = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formCitacao),
        });
        if (!r.ok) throw new Error();
        const salva = await r.json();
        if (isEdit) Object.assign(this.itemCitacao, salva);
        else        this.citacoes.push(salva);
        this.fecharCitacao();
        this.mostrarToast(isEdit ? 'Citação atualizada!' : 'Citação adicionada!');
      } catch {
        this.mostrarToast('Erro ao salvar.', 'erro');
      }
    },

    async removerCitacao(item) {
      if (!confirm('Remover citação?')) return;
      try {
        const r = await fetch(`/api/citacoes/${item.id}`, { method: 'DELETE' });
        if (!r.ok) throw new Error();
        this.citacoes = this.citacoes.filter(c => c.id !== item.id);
      } catch {
        this.mostrarToast('Erro ao remover.', 'erro');
      }
    },

    mostrarToast(msg, tipo = 'ok') {
      clearTimeout(this._toastTimer);
      this.toast = { msg, tipo };
      this._toastTimer = setTimeout(() => { this.toast = { msg: '', tipo: 'ok' }; }, 3000);
    },
  };
}
