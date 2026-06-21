function app() {
  return {
    tabs: {
      filmes:  { label: 'Filmes',  emoji: '🎬' },
      series:  { label: 'Séries',  emoji: '📺' },
      livros:  { label: 'Livros',  emoji: '📚' },
    },
    tipo: 'filmes',
    listaIds: { filmes: null, series: null, livros: null },
    listas:   { filmes: null,  series: null,  livros: null },
    carregando: false,

    buscaAberta: false,
    termoBusca: '',
    resultadosBusca: [],
    buscando: false,
    _debounce: null,

    notasAbertas: false,
    itemNotas: null,
    formNotas: { nota: null, comentario: '' },

    toast: { msg: '', tipo: 'ok' },
    _toastTimer: null,

    async init() {
      this.carregando = true;
      try {
        const r = await fetch('/api/listas/');
        const todas = await r.json();
        const mapa = { 'Filmes': 'filmes', 'Séries': 'series', 'Livros': 'livros' };
        for (const l of todas) {
          const t = mapa[l.nome];
          if (t) this.listaIds[t] = l.id;
        }
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
      return this.listas[this.tipo]?.filmes || [];
    },

    get listaAtivaId() {
      return this.listaIds[this.tipo];
    },

    async trocarTipo(novoTipo) {
      if (this.tipo === novoTipo && !this.buscaAberta) return;
      this.fecharBusca();
      this.tipo = novoTipo;
      if (!this.listas[novoTipo]) {
        this.carregando = true;
        try { await this._carregarLista(novoTipo); }
        finally { this.carregando = false; }
      }
    },

    abrirBusca() {
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

    mostrarToast(msg, tipo = 'ok') {
      clearTimeout(this._toastTimer);
      this.toast = { msg, tipo };
      this._toastTimer = setTimeout(() => { this.toast = { msg: '', tipo: 'ok' }; }, 3000);
    },
  };
}
