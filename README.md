# Midnight Detailing

Website institucional da **Midnight Detailing** — auto detailing premium em Portugal.

Stack: Django 5.2 · Python 3.11+ · SQLite (dev).

---

## Setup local (Windows)

> Requer Python 3.11 ou superior. Confirma com `python --version`.

```powershell
# 1. Clonar / abrir a pasta
cd C:\Users\TDJ-C\Documents\Projects\midnight_detailing

# 2. Criar e activar o virtualenv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Copiar variáveis de ambiente
copy .env.example .env

# 5. Aplicar migrations
python manage.py migrate

# 6. Criar superuser para o admin
python manage.py createsuperuser

# 7. Correr o servidor de desenvolvimento
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` para ver o site e `http://127.0.0.1:8000/admin/` para entrar no painel.

> **Git Bash / WSL:** substitui `.\venv\Scripts\Activate.ps1` por `source venv/Scripts/activate` e `copy` por `cp`.

---

## Estrutura

```
midnight_detailing/
├── manage.py
├── requirements.txt
├── .env.example          # template das variáveis de ambiente
├── midnight/             # projecto Django (settings, urls, wsgi/asgi)
├── core/                 # app principal: views, models, admin, forms
├── templates/            # templates partilhados + core/
├── static/               # css, js, img (servidos em dev)
├── media/                # uploads (criado em runtime)
└── locale/               # traduções (pt-PT)
```

---

## Variáveis de ambiente

Definidas em `.env` (não commitado). Ver `.env.example` para a lista completa.

| Variável | Default dev | Notas |
|---|---|---|
| `DJANGO_SECRET_KEY` | inseguro, só dev | Obrigatório em produção |
| `DJANGO_DEBUG` | `True` | `False` em produção |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Lista separada por vírgulas |
| `DJANGO_EMAIL_BACKEND` | consola | SMTP em produção |
| `CONTACT_EMAIL` | `geral@midnightdetailing.pt` | Destino do formulário de contacto |

Em desenvolvimento o email do formulário aparece na consola do `runserver` — não é enviado.

---

## Localização

- `LANGUAGE_CODE = 'pt-pt'`
- `TIME_ZONE = 'Europe/Lisbon'`
- Admin em português.

---

## Comandos úteis

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic    # gera ./staticfiles em produção
python manage.py test
```
