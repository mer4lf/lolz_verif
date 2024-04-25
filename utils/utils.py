deals_per_page = 10


def is_card(number: str):
    if number.isdigit() and len(number) == 16:
        return True
    return False


def export_tags(keyboard):
    texts = []
    for i in keyboard:
        for j in i:
            texts.append(j.text)
    # done_tags = [i if i[::len(i) - 1] == "··" else "" for i in texts]
    done_tags = []
    for i in texts:
        if len(i) > 2:
            if i[::len(i) - 1] == "··":
                done_tags.append(i[2:-2])
    return ", ".join(done_tags)


MoneyWays = {
    'sber': 'Сбербанк',
    'tink': 'Тинькофф',
    'usdt': 'USDT',
    'eth': 'Etherium'
}

Ways = {
    'cards': 'название банка карты, которую вы хотите привязать',
    'crypto': 'адрес криптокошелька в сети USDT, который вы хотите привязать',
    'lolz': 'свой ник на форуме Lolzteam',
    'umoney': 'реквизиты своего счета Юмани'
}

ProjectTypes = {
    'type_0': '0',
    'type_1': '1',
    'type_2': '2'
}

ReputationTypes = {
    '🔴': 0,
    '🟡': 1,
    '🟢': 2,
}
