class EmailEscaping:
    def __init__(self, symbol: str, email=None):
        self.default_email = email
        self.symbol = symbol
        if email is None:
            self.email_escaping = 'Вы не указали Email при инициализации класса, используйте функцию ' \
                                  'EmailEscaping.set_email для экранирования'
        else:
            self.email_escaping = self._escaping()

    def set_email(self, email):
        self.default_email = email
        return self._escaping()

    def _escaping(self):
        if '@' in self.default_email:
            email_index = self.default_email.split('@')
            total_symbol = len(email_index[0])
            email_index[0] = total_symbol * self.symbol
            email_index = '@'.join(email_index)
            self.email_escaping = email_index
            return self.email_escaping
        else:
            return f"Некорректный Email {self.default_email}"


class PhoneEscaping:
    def __init__(self, symbol: str, number, phone=None):
        self.default_phone = phone
        self.number = int(number)  # Eсли закинули число str
        self.symbol = symbol
        if phone is None:
            self.phone_escaping = 'Вы не указали номер Phone при инициализации класса, используйте функцию ' \
                                  'PhoneEscaping.set_phone для экранирования'
        else:
            self.phone_escaping = self._escaping()

    def set_phone(self, phone):
        self.default_phone = phone
        return self._escaping()

    def _escaping(self):
        number = self.number
        phone_index = self.default_phone.split(' ')
        phone_index = [index for index in phone_index if index]  # Очищаем пустые элементы
        phone_index.reverse()  # разворачиваем список, нужно же последнии цефры экранировать
        for item in phone_index:
            if number == 0 or number < 0:  # проверка если менять ничего не надо)
                break
            index = phone_index.index(item)
            item = item[::-1]  # разворот строки
            for elem in item:
                if number == 0:  # выход по окончанию замен
                    item = item[::-1]  # обратный разворот если заменилось меньше элементов
                    phone_index[index] = item
                    break
                item = item.replace(elem, self.symbol, 1)  # замена элемента в строке в колличестве 1шт
                number -= 1

            phone_index[index] = item
        phone_index.reverse()
        self.phone_escaping = ' '.join(phone_index)
        return self.phone_escaping


if __name__ == '__main__':
    # Task 1.1 - Email
    # email = EmailEscaping('x', 'sasha.com-09@mail.ru')
    # print(email.email_escaping)
    # # Либо так
    # email = EmailEscaping('x')
    # print(email.email_escaping)  # Отлавливание на: не указание аргумента email при инициализации класса
    # print(email.set_email('09@mail.ru'))
    # ______________________________________________________________________

    # Task 1.1 - Phone
    phone = PhoneEscaping('x', 2, '+7 123   456      7891')
    print(phone.phone_escaping)
    # Либо так
    phone = PhoneEscaping('x', 5)
    print(phone.phone_escaping)  # Отлавливание на: не указание аргумента email при инициализации класса
    print(phone.set_phone('+7 1234 567 891'))
    # _______________________________________________________________________

    # Task 1.1 - Skype

