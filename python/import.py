import settings
import ynab_client
import click
import csv
import numbers
import settings as settings_module
from functions import create_transaction_from_csv
from qifparse.parser import QifParser

from pynYNAB.exceptions import WrongPushException

@click.command()
@click.option('--account', prompt='Your YNAB Account Name')
@click.option('--path', prompt='The CSV file')
def import_csv(account, path):
    """Import a CSV into YNAB"""

    click.echo('Pulling from YNAB')
    ynab_client.init()
    ynab_client.sync()

    expected_delta = 0

    ynab_account = ynab_client.getaccount(account)
    if not ynab_account:
        click.echo('Account does not exist')
        return

    # Building up data
    with open(path, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            create = create_transaction_from_csv(row, ynab_account)
            if isinstance(create, numbers.Number):
                expected_delta += create
                print 'Adding Transaction or Payee'
            else:
                print create['error']

    if expected_delta > 0:
        print 'Pushing to YNAB'
        try:
            ynab_client.client.push(expected_delta)
        except WrongPushException, ex:
            print 'Push failed'
            print ex.msg

if __name__ == '__main__':
    import_csv()
