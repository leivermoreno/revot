# Revot

Telegram bot for the purpose of automating banking transactions such as account balance consulting and money transfers (currently only balance consulting) via telegram bot commands.
The actual Banking automation is handled by the submodule mercantil_automatiom, also developed by me. The bank in question is Banco Mercantil.

## Requirements

- The balance command prompts for a passcode to access it (could also grant access only to whitelisted IDs but decided to take this approach), whose message is deleted once received by the bot, for security reasons. It is stored in the secret.yaml file along with the Bot Token.

- The login-info.yaml file required by the submodule stores the login credentials to access the bank portal.

You can take a look at the examples files secret-dev and login-data
