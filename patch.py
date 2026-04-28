
with open("static/css/style.css", "a") as f:
    f.write("
/* Vercel Pure Black Theme Overrides */
:root { --bs-body-bg: #000000 !important; --bs-body-color: #EDEDED !important; --bs-tertiary-bg: #0A0A0A !important; --bs-secondary-bg: #111111 !important; --bs-border-color: #222222 !important; --bs-primary: #FFD400 !important; --trading-yellow: #FFD400 !important; --bs-link-color: #FFD400 !important; }
body { background-color: #000000 !important; color: #EDEDED !important; }
.navbar, .bg-dark { background-color: #000000 !important; border-bottom: 1px solid #222 !important; }
.card { background-color: #0A0A0A !important; border: 1px solid #222 !important; box-shadow: none !important; }
.card-header { background-color: #0A0A0A !important; border-bottom: 1px solid #222 !important; color: #EDEDED !important; }
.text-muted, .text-secondary { color: #A1A1AA !important; }
.table { color: #EDEDED !important; }
.table th { border-bottom: 1px solid #222 !important; color: #A1A1AA !important; }
.table td { border-bottom: 1px solid #222 !important; color: #EDEDED !important; }
.table-hover tbody tr:hover { background-color: #111111 !important; }
.trading-log { background-color: #000000 !important; border: 1px solid #222 !important; }
.btn-primary { background-color: #EDEDED !important; color: #000000 !important; border-color: #EDEDED !important; }
.btn-primary:hover { background-color: #ffffff !important; color: #000000 !important; }
.btn-outline-primary { color: #EDEDED !important; border-color: #333 !important; }
.btn-outline-primary:hover { background-color: #EDEDED !important; color: #000000 !important; }
.nav-link.active, .nav-link:hover { color: #FFD400 !important; }
footer.bg-dark { border-top: 1px solid #222 !important; }
.badge.bg-success { background-color: #FFD400 !important; color: #000000 !important; }
")

