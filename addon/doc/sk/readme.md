# VoiceToggle

## Úvod

Doplnok VoiceToggle pre odčítač obrazovky NVDA umožňuje predvoliť si ľubovoľné množstvo hlasov v jeho nastavení, a potom sa medzi týmito hlasmi môžete kedykoľvek rýchlo prepínať v kruhu pomocou jednoduchej a jedinej klávesovej skratky NVDA + Alt + V .

## Ukážkový príklad

Povedzme, že hovoríte po slovensky a anglicky. Potom si môžete v nastavení doplnku VoiceToggle pridať dva hlasy, ako je popísané nižšie, jeden s slovenskou a druhý s anglickou výslovnosťou. Potom sa môžete kedykoľvek prepínať medzi týmito dvoma hlasmi pomocou jedinej, jednoduchej a pohodlnej klávesovej skratky NVDA + Alt + V namiesto toho, aby ste museli pracne používať kruh nastavenia hlasového výstupu, dialóg nastavenia hlasového výstupu alebo meniť hlasový výstup v kategórii reč pomocou dialógu nastavenia NVDA.

## Konfigurácia hlasov

Nasledujúcim postupom môžete cez nastavenie VoiceToggle predvoliť hlasy, medzi ktorými sa má VoiceToggle prepínať:

1. Stlačením kláves NVDA + N otvorte ponuku NVDA.
2. Zvoľte podponuku "Možnosti".
3. Zvoľte položku "Nastavenia".
4. Prejdite do kategórie "VoiceToggle". Otvorí sa strana nastavenia doplnku VoiceToggle a zoznam hlasov bude obsahovať iba aktuálny hlas.
5. Ak chcete do zoznamu hlasov pridať ďalší hlas, otvorte dialógové okno pre pridanie hlasu pomocou tlačidla "Pridať hlas".
6. Pomocou prvého zoznamového rámiku vyberte najprv požadovaný hlasový výstup, a potom pomocou druhého zoznamového rámiku vyberte požadovaný hlas v rámci zvoleného hlasového výstupu, ktorý chcete pridať, a stlačte tlačidlo "Pridať". Práve pridaný hlas sa objaví v zozname hlasov za aktuálne vybranou položkou v zozname.
7. Nezabudnite vykonané nastavenie uložiť stlačením tlačidla "OK" alebo "Použiť" na konci dialógového okna nastavenia NVDA.

## Ďalšie nastavenia

Môžete ovplyvniť, či zmena aktuálneho hlasu prostredníctvom kruhu nastavenia hlasového výstupu, dialógu nastavenia hlasového výstupu alebo pomocou kategórie reč v dialógu nastavenia NVDA tiež zodpovedajúcim spôsobom aktualizuje hlas predvolený v nastavení VoiceToggle. Toto je možné ovplyvniť v nastavení VoiceToggle cez začiarkavacie políčko "Aktualizovať hlas pri jeho zmene cez nastavenie reči samotného NVDA".

## Zapamätanie si hlasov pre jednotlivé aplikácie

Povedzme, že chcete prechádzať webové stránky v angličtine, ale poznámky a všetku ďalšiu prácu chcete robiť v slovenčine. V takom prípade je možné docieliť zapamätanie si naposledy použitého hlasu pre vybrané aplikácie. Keď napríklad prepnete do prehliadača Google Chrome, hlas sa automaticky prepne na naposledy použitý hlas v tejto aplikácii, napríklad do angličtiny. Keď sa potom vrátite do inej aplikácie, napríklad do aplikácie Microsoft Word, aby ste si zapísali poznámky v slovenčine, tak sa hlas prepne späť na tento predvolený slovenský hlas. Toto správanie je umožnené vďaka funkcii konfiguračných profilov dostupné v NVDA.

Ak chcete nastaviť určitú aplikáciu tak, aby si pamätala v nej naposledy použitý hlas, tak postupujte podľa nasledujúcich krokov:

1. Prepnite sa do danej aplikácie, napríklad do prehliadača Google Chrome.
2. Stlačením kláves NVDA + N otvorte ponuku NVDA.
3. Vyberte položku "Konfiguračné profily".
4. Stlačte tlačidlo "Nový".
5. Prejdite na prepínač pomenovaný ako "Ručná aktivácia" v zoskupení "Aktivovať" a prepnite ho pomocou šípky dole na hodnotu "Aktuálna aplikácia".
6. Vytvorenie konfiguračného profilu potvrďte tlačidlom "OK".

## Zmena klávesovej skratky pre prepínanie hlasov

Nasledujúcim spôsobom je možné predvolenú klávesovú skratku NVDA + Alt + V pre prepínanie hlasov prípadne zmeniť na inú vami viac vyhovujúcu skratku:

1. Stlačením kláves NVDA + N otvorte ponuku NVDA.
2. Zvoľte podponuku "Možnosti".
3. Vyberte položku "Klávesové skratky".
4. Do editačného poľa "Filter" zadajte "nasledujúci hlas".
5. V stromovom zobrazení prejdite na položku "Prepne na nasledujúci hlas” v kategórii "Ostatné".
6. Aktivujte tlačidlo "Pridať", potom stlačte požadovanú klávesovú skratku a potvrďte klávesom Enter.
7. Pridanie skratky potvrďte tlačidlom "OK".

## História verzií

[Históriu verzií doplnku VoiceToggle je možné zobraziť v angličtine tu][changelog].

## Spätná väzba a kontakt

Ak zistíte nejaké nedostatky, prípadne ak máte nápady na zlepšenie doplnku VoiceToggle alebo iné komentáre, tak vám budem počúvať na emailovej adrese [adam.samec@gmail.com](mailto:adam.samec@gmail.com)

Využiť môžete tiež možnosti [repositára doplnku VoiceToggle na serveri GitHub][GitHub], napríklad tamojšie [nahlasovanie chýb][GitHub issue].

## Licencia

Doplnok VoiceToggle je dostupný pod licenciou GNU General Public License verzie 2.0.

[changelog]: https://github.com/adamsamec/VoiceToggle/blob/main/Changelog.md
[GitHub]: https://github.com/adamsamec/VoiceToggle
[GitHub issue]: https://github.com/adamsamec/VoiceToggle/issues