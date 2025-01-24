import SFPO_config


def print_SFPO_01():
    print("SFPO_01")
    print("-Rootstr-: " + str(SFPO_config.rootstr))
    print("-Filename-: " +
          str(SFPO_config.filenames))
    print("So viele Dateien sind im Ordner -Filename-: " +
          str(len(SFPO_config.filenames)))
    print("Rootname: " + str(SFPO_config.rootname))
    print("Mainfolder: " + str(SFPO_config.mainfolder))
    print("\n")


def print_SFPO_02():
    print("SFPO_02")
    print("Erfolgreicher Pull-Out: " + str(SFPO_config.acceptresults))
    print("Typ: " + str(type(SFPO_config.acceptresults)))
    print("Anzahl: " + str(len(SFPO_config.acceptresults)))
    print("Erfolglose Pull-Out: " + str(SFPO_config.abortresults))
    print("Typ: " + str(type(SFPO_config.abortresults)))
    print("Anzahl: " + str(len(SFPO_config.abortresults)))
    print("Pull-Outs gesamt: " + (str(SFPO_config.acceptresults) +
                str(SFPO_config.abortresults)))
    print("Anzahl: " + str(len(SFPO_config.abortresults) +
                           len(SFPO_config.acceptresults)))
    print("Kraft am Faserkink sind: " + str(SFPO_config.forcefiberkinks))
    print("Durchschnitt amFaserdurchmesser ist: " + str(SFPO_config.fiberdmean) +
          "+-" + str(SFPO_config.fiberdmeanstdv))
    print("\n")


def print_SFPO_03():
    print("SFPO_03")
    print("Max Force= " + str(SFPO_config.maxforces))
    print("Max embedding length= " + str(SFPO_config.embeddinglength))
    print("IFSS sind= " + str(SFPO_config.ifss))
    print("Die gesamte Arbeit beträgt: " + str(SFPO_config.wtotal))
    print("Die Intervalle der Arbeit betragen: " + str(SFPO_config.wintervall))
    print("Das SFPO Verhältnis: " + str(SFPO_config.fiberratioresult))
    print("Scheinbare IFSS " + str(SFPO_config.ifss))
    print("Durchschnittlich alles:\n"
          + "     Kraft: " + str(SFPO_config.meanforce) +
          ' +- '+ str(SFPO_config.forcestdv) +
          ' ->' + str(SFPO_config.forcerelstdv) + '%'  + "\n"
          + "     Arbeit: " + str(SFPO_config.meanwork) +
           ' +- ' + str(SFPO_config.workstdv) +
          ' ->' + str(SFPO_config.workrelstdv) + '%' + "\n"
          + "     IFSS: " + str(SFPO_config.meanifss) +
          ' +- '+ str(SFPO_config.ifssstdv) +
          ' ->' + str(SFPO_config.ifssrelstdv) + '%' + "\n"
          )
    print("Einbettlaenge: " + str(SFPO_config.embeddinglength))
    print(SFPO_config.tenthints)

def print_Besonderes():
    print(SFPO_config.maxforces)
    print("\n")
    print(SFPO_config.maxforce_indices)
    print("\n")
    print(SFPO_config.integral_bis_maximal)
    print("\n")
    print(SFPO_config.integrale_nach_maximal)
    print("\n")
    print(SFPO_config.gesamtintegrale)
    print("\n")
    print(SFPO_config.mainfolder)
