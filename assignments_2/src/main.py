from src.domain.money import Money
from src.domain.payment import Payment
from src.interface.cli import CLI
from src.environment.menus import create_menus

budget = 10_000

def main():
    menus = create_menus()


    payment = Payment(Money(budget))

    cli = CLI(
        menus=menus,
        inventory=intventory,
        payment=payment,
    )

    cli.run()

if __name__ == "__main__":
    main()