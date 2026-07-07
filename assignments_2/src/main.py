from src.domain.money import Money
from src.domain.payment import Payment
from src.interface.cli import CLI

budget = 10_000

def main():
    menus = [
    ]


    payment = Payment(Money(budget))

    cli = CLI(
        menus=menus,
        inventory=intventory,
        payment=payment,
    )

    cli.run()

if __name__ == "__main__":
    main()