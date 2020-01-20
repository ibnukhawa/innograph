def Terbilang(amount_total):
    '''function to create total terbilang for amount_total'''

    unit = ["", "Satu", "Dua", "Tiga", "Empat",
            "Lima", "Enam", "Tujuh", "Delapan",
            "Sembilan", "Sepuluh", "Sebelas"]
    result = " "

    amt = int(amount_total)
    if amt >= 0 and amt <= 11:
        result = result + unit[amt]
    elif amt < 20:
        result = Terbilang(amt % 10) + " Belas"
    elif amt < 100:
        result = Terbilang(amt / 10) + " Puluh" + Terbilang(amt % 10)
    elif amt < 200:
        result = " Seratus" + Terbilang(amt - 100)
    elif amt < 1000:
        result = Terbilang(amt / 100) + " Ratus" + Terbilang(amt % 100)
    elif amt < 2000:
        result = " Seribu" + Terbilang(amt - 1000)
    elif amt < 1000000:
        result = Terbilang(amt / 1000) + " Ribu" + Terbilang(amt % 1000)
    elif amt < 1000000000:
        result = Terbilang(amt / 1000000) + " Juta" + Terbilang(amt % 1000000)
    elif amt < 1000000000000:
        result = Terbilang(amt / 1000000000) + " Miliar" \
            + Terbilang(amt % 1000000000)
    else:
        result = Terbilang(amt / 1000000000000) + " Triliun" \
            + Terbilang(amt % 1000000000000)
    return result