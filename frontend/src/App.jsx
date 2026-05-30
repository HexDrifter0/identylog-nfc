import { useState } from 'react';

function App() {
  const [publicToken, setPublicToken] = useState('');
  const [activateToken, setActivateToken] = useState('');

  const handlePublicSubmit = (event) => {
    event.preventDefault();
    if (!publicToken.trim()) return;
    globalThis.location.href = `/t/${publicToken.trim()}/`;
  };

  const handleActivateSubmit = (event) => {
    event.preventDefault();
    if (!activateToken.trim()) return;
    globalThis.location.href = `/activar/${activateToken.trim()}/`;
  };

  return (
    <div className="page-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Identylog NFC</p>
          <h1>Tu memoria NFC, lista para activar</h1>
          <p>
            Usa esta interfaz para abrir el registro, iniciar sesión o navegar a la vista pública
            de tu soporte NFC.
          </p>
          <div className="button-group">
            <a className="button" href="/registro/">Registrarse</a>
            <a className="button button-outline" href="/login/">Iniciar sesión</a>
            <a className="button button-outline" href="/dashboard/">Mi panel</a>
          </div>
        </div>
      </header>

      <main>
        <section className="card">
          <h2>Ver una página pública</h2>
          <p>Introduce el token público para abrir la página de tu soporte NFC.</p>
          <form onSubmit={handlePublicSubmit}>
            <label htmlFor="public-token">Token público</label>
            <input
              id="public-token"
              type="text"
              value={publicToken}
              onChange={(event) => setPublicToken(event.target.value)}
              placeholder="Ej: abc123XYZ"
            />
            <button className="button" type="submit">Abrir token público</button>
          </form>
        </section>

        <section className="card">
          <h2>Activar soporte NFC</h2>
          <p>Introduce el token para ir a la pantalla de activación.</p>
          <form onSubmit={handleActivateSubmit}>
            <label htmlFor="activate-token">Token de soporte</label>
            <input
              id="activate-token"
              type="text"
              value={activateToken}
              onChange={(event) => setActivateToken(event.target.value)}
              placeholder="Ej: abc123XYZ"
            />
            <button className="button" type="submit">Ir a activar</button>
          </form>
          <small>
            Si ya conoces el código de activación, podrás introducirlo en la vista del backend.
          </small>
        </section>

        <section className="card">
          <h2>Recuerda</h2>
          <ul>
            <li>La cuenta se crea en <a href="/registro/">/registro/</a></li>
            <li>El acceso se realiza en <a href="/login/">/login/</a></li>
            <li>Tu panel está en <a href="/dashboard/">/dashboard/</a></li>
          </ul>
        </section>
      </main>

      <footer className="footer">
        <p>El backend de Django ya gestiona las rutas y los formularios reales.</p>
      </footer>
    </div>
  );
}

export default App;
