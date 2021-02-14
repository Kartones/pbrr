from colorama import Fore, Style, deinit


class Log:
    @staticmethod
    def error_and_exit(message: str) -> None:
        print(Fore.RED + message + Style.RESET_ALL)
        deinit()
        exit(1)

    @staticmethod
    def warn(message: str) -> None:
        print(Fore.YELLOW + message + Style.RESET_ALL)

    @staticmethod
    def warn_and_raise_error(message: str) -> None:
        Log.warn(message)
        raise ValueError(message)

    @staticmethod
    def info(message: str) -> None:
        print(Style.DIM + Fore.WHITE + message + Style.RESET_ALL)
