from .core import VacationExtender

def main():
    ve = VacationExtender('test/config.toml')
    ve.run()
    print(ve)
