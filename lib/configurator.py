import json
import os
from lib.prompt import prompt_confirmation
from lib.wallet import wallet


class configurator:
    """
    Allows the load and creation of a params.json file
    """

    def __init__(self):
        self.params_file = os.getcwd() + "/params.json"
        self.ticker = None
        self.wallet_data_dir = None
        self.wallet_cli_path = None
        self.alias_prefix = None
        self.headers = None
        self.new_txs = None

    def load(self):

        if os.path.exists(self.params_file) and os.stat(self.params_file).st_size != 0:
            print("\n#### Reading params.json\n")
            with open(self.params_file) as json_file:
                loaded_params = json.load(json_file)
            if "ticker" in loaded_params:
                self.ticker = loaded_params["ticker"]
                print("'{}' found : {}".format("ticker", self.ticker))
            else:
                print("Missing param 'ticker' in the params.json")
                self.set_ticker()
            if "wallet_data_dir" in loaded_params and loaded_params["wallet_data_dir"] != "":
                self.wallet_data_dir = loaded_params["wallet_data_dir"]
                print("'{}' found : {}".format("wallet_data_dir", self.wallet_data_dir))
            if "wallet_cli_path" in loaded_params and loaded_params["wallet_cli_path"] != "":
                self.wallet_cli_path = loaded_params["wallet_cli_path"]
                print("'{}' found : {}".format("wallet_cli_path", self.wallet_cli_path))
            if "alias_prefix" in loaded_params and loaded_params["alias_prefix"] != "":
                self.alias_prefix = loaded_params["alias_prefix"]
                print("'{}' found : {}".format("alias_prefix", self.alias_prefix))
            else:
                print("Missing param 'alias_prefix' in the params.json")
                self.set_alias_prefix()
            if "headers" in loaded_params:
                self.headers = loaded_params["headers"]
                print("'{}' found : {}".format("headers", self.headers))
            else:
                print("Missing param 'headers' in the params.json. Attempting to retrieve.")
                self.set_header()
            if "new_txs" in loaded_params and loaded_params["new_txs"] != []:
                self.new_txs = loaded_params["new_txs"]
                print("'{}' found : {}".format("new_txs", self.new_txs))
            else:
                print("Missing param 'new_txs' in the params.json")
                self.set_new_txs()
            self.save_params_json()
        else:
            print("#### Missing or empty params.json file starting configuration mode\n")
            self.prompt_params_creation()
            self.save_params_json(reload=True)

    def prompt_params_creation(self):

        self.set_ticker()
        self.set_alias_prefix()
        self.set_header()
        if prompt_confirmation("Do you want to setup the wallet interface ? (y/n) : "):
            self.set_new_txs()

    def save_params_json(self, reload=False):

        # As during load the whole headers param is stored in self.headers a check is needed
        # to avoid writing another dict inside the existing one
        _api_key = self.headers["IHOSTMN-API-KEY"] if "IHOSTMN-API-KEY" in self.headers else self.headers

        params = {
            "ticker": self.ticker,
            "wallet_data_dir": self.wallet_data_dir,
            "wallet_cli_path": self.wallet_cli_path,
            "alias_prefix": self.alias_prefix,
            "headers": {"IHOSTMN-API-KEY": _api_key},
            "new_txs": self.new_txs
        }

        with open(self.params_file, 'w') as json_file:
            json.dump(params, json_file, indent=4)

        print("params.json successfully saved\n")

        if reload:
            self.load()

    def set_ticker(self):
        # Ticker
        while not self.ticker:
            self.ticker = input("Input ticker (ex.: SAPP): ").upper()
        return self.ticker

    def set_alias_prefix(self):
        # Alias prefix
        inp_alias = input("Input alias prefix for masternodes (Press enter for default = 'MN') : ").upper()
        self.alias_prefix = "MN" if not inp_alias else inp_alias
        return self.alias_prefix

    def set_header(self):
        # IHOSTMN-API-KEY
        while not self.headers:
            self.headers = input("Input your IHOSTMN-API-KEY : ")
        return self.headers

    def set_new_txs(self):
        # Transactions list for MN creation
        if self.wallet_data_dir and self.wallet_cli_path:
            wallet_handle = wallet(data_dir=self.wallet_data_dir, cli_path=self.wallet_cli_path)
            if wallet_handle.check_server():
                self.new_txs = json.loads(wallet_handle.get_masternode_outputs())
            else:
                print("Cannot connect to wallet. please check your wallet configuration.\n")
                self.new_txs = []
        else:
            if prompt_confirmation("Do you wish to setup the wallet handles now ? (y/n) : "):
                self.set_wallet_handles()
            else:
                self.new_txs = []
        return self.new_txs

    def set_wallet_handles(self):
        # Setup the wallet handle to get transaction from the wallet
        if not self.wallet_data_dir:
            self.set_wallet_data_dir()
        if not self.wallet_cli_path:
            self.set_wallet_cli_path()

        if not self.wallet_data_dir or not self.wallet_cli_path:
            if prompt_confirmation("The paths you entered to the data directory and cli binary are empty !\n"
                                   "Do you wish to cancel wallet setup ? (y/n) : "):
                pass
            else:
                self.set_wallet_handles()
        else:
            self.set_new_txs()

    def set_wallet_data_dir(self):
        _input = input("Input the path to {} data directory : ".format(self.ticker))
        self.wallet_data_dir = _input if _input != "" else None
        return self.wallet_data_dir

    def set_wallet_cli_path(self):
        _input = input("Input the path to the {} cli binary : ".format(self.ticker))
        self.wallet_cli_path = _input if _input != "" else None
        return self.wallet_cli_path