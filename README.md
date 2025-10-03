# Totp-bot
### Installing
<p>Open <code>.env.example</code> file then set <code>TOKEN=</code> from [BotFather](https://t.me/BotFather) and your telegram<code>USER_ID</code>
You can get your TELEGRAM ID  via <code>/start</code> command in bot
</p>

	mv .env.example .env
	python3 -m venv env
	source env/bin/activate
	pip install -r requirements.txt
	python main.py

### Using
`/add` command adds code generator via totp secret

`/list` command shows all totp secrets available

`/totp` generate totp_code
