import random

def giochino(sss):
    x = 0
    y = int(sss)
    numeroScelto = random.randint(x,y)

    while True:
        print("Quale numero ho pensato da " + str(x) + " a " + str(y) + "?:\n")
        numeroTuo = input("Vai scegli: ")

        if (int(numeroTuo) == int(numeroScelto)):
            print("GRANDISSIMO ERA ESATTAMENTE IL NUMERO " + str(numeroScelto))
            break
        else:
            print("*EERHM* ERRORE no sei scarso, ritenta")