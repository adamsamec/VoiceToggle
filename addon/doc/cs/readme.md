# VoiceToggle

## Úvod

Doplněk VoiceToggle pro odečítač obrazovky NVDA umožňuje předvolit si libovolné množství hlasů v jeho nastavení, a poté se mezi těmito hlasy můžete kdykoliv rychle přepínat v kruhu pomocí jednoduché a jediné klávesové zkratky NVDA + Alt + V .

## Ukázkový příklad

Řekněme, že mluvíte česky a anglicky. Pak si můžete v nastavení doplňku VoiceToggle přidat dva hlasy, jak je popsáno níže, jeden s českou a druhý s anglickou výslovností. Poté se můžete kdykoliv přepínat mezi těmito dvěma hlasy pomocí jediné, jednoduché a pohodlné klávesové zkratky NVDA + Alt + V místo toho, abyste museli pracně používat kruh nastavení hlasového výstupu, dialog nastavení hlasového výstupu nebo měnit hlasový výstup v kategorii řeč pomocí dialogu nastavení NVDA.

## Konfigurace hlasů

Následujícím postupem můžete přes nastavení VoiceToggle předvolit hlasy, mezi kterými se má VoiceToggle přepínat:

1. Stisknutím kláves NVDA + N otevřete nabídku NVDA.
2. Zvolte podnabídku „Možnosti“.
3. Zvolte položku „Nastavení“.
4. Přejděte do kategorie „VoiceToggle“. Otevře se karta nastavení doplňku VoiceToggle a seznam hlasů  bude obsahovat pouze aktuální hlas.
5. Chcete-li do seznamu hlasů přidat další hlas, otevřete dialogové okno pro přidání hlasu  pomocí tlačítka „Přidat hlas”.
6. Pomocí prvního rozbalovacího políčka vyberte nejprve požadovaný hlasový výstup, a poté pomocí druhého rozbalovacího políčka vyberte požadovaný hlas v rámci zvoleného hlasového výstupu, který chcete přidat, a stiskněte tlačítko „Přidat“. Právě přidaný hlas se objeví v seznamu hlasů za aktuálně vybranou položkou v seznamu.
7. Nezapomeňte provedené nastavení uložit stisknutím tlačítka „OK“ nebo „Použít“ na konci dialogového okna nastavení NVDA.

## Další nastavení

Můžete ovlivnit, jestli změna aktuálního hlasu prostřednictvím kruhu nastavení hlasového výstupu, dialogu nastavení hlasového výstupu nebo pomocí kategorie řeč v dialogu nastavení NVDA také odpovídajícím způsobem aktualizuje hlas předvolený v nastavení VoiceToggle. Toto lze ovlivnit v nastavení VoiceToggle přes zaškrtávací políčko "Aktualizovat hlas při jeho změně přes kruh nastavení hlasového výstupu, dialog nastavení hlasového výstupu nebo přes kategorii řeč v dialogu nastavení NVDA".

## Zapamatování si hlasů pro jednotlivé aplikace

Řekněme, že chcete procházet webové stránky  v angličtině, ale poznámky a veškerou další práci chcete dělat v češtině. V takovém případě je možné docílit zapamatování si naposledy použitého hlasu pro vybrané aplikace. Když například přepnete do prohlížeče Google Chrome, hlas se automaticky přepne na naposledy použitý hlas v této aplikaci, například do angličtiny. Když se pak vrátíte do jiné aplikace, například do aplikace Microsoft Word, abyste si zapsali poznámky v češtině, tak se hlas přepne zpět na tento výchozí český hlas. Toto chování je umožněno díky funkci konfiguračních profilů dostupné v NVDA.

Chcete-li nastavit určitou aplikaci tak, aby si pamatovala v ní naposledy použitý hlas, tak postupujte podle následujících kroků:

1. Přepněte se do dané aplikace, například do prohlížeče Google Chrome.
2. Stisknutím kláves NVDA + N otevřete nabídku NVDA.
3. Vyberte položku „Konfigurační profily“.
4. Stiskněte tlačítko „Nový“.
5. Přejděte na přepínač pojmenovaný jako „Aktivace“ v seskupení „Použít tento profil pro“ a přepněte jej pomocí šipky dolů na hodnotu „Aktuální aplikace“.
6. Vytvoření konfiguračního profilu potvrďte tlačítkem „OK“.

## Změna klávesové zkratky pro přepínání hlasů

Následujícím způsobem lze výchozí klávesovou zkratku NVDA + Alt + V pro přepínání hlasů případně změnit na jinou vámi více vyhovující zkratku:

1. Stisknutím kláves NVDA + N otevřete nabídku NVDA.
2. Zvolte podnabídku „Nastavení“.
3. Vyberte položku „Klávesové příkazy“.
4. Do editačního pole „Filtrovat podle“ zadejte „následující hlas“.
5. Ve stromovém zobrazení přejděte na položku „Přepne na následující hlas” v kategorii „Různé“.
6. Aktivujte tlačítko „Přidat“, poté stiskněte požadovanou klávesovou zkratku a potvrďte klávesou Enter.
7. Přidání zkratky potvrďte tlačítkem „OK“.

## Historie verzí

[Historii verzí doplňku VoiceToggle lze zobrazit v angličtině zde][changelog].

## Zpětná vazba a kontakt

Shledáte-li nějaké nedostatky, případně máte-li nápady na zlepšení doplňku VoiceToggle nebo jiné komentáře, tak vám budu naslouchat na emailové adrese [adam.samec@gmail.com](mailto:adam.samec@gmail.com)

Využít můžete také možností [repositáře doplňku VoiceToggle na serveru GitHub][GitHub], například tamní [nahlašování chyb][GitHub issue].

## Licence

Doplněk VoiceToggle je dostupný pod licencí GNU General Public License version 2.0.

[changelog]: https://github.com/adamsamec/VoiceToggle/blob/main/Changelog.md
[GitHub]: https://github.com/adamsamec/VoiceToggle
[GitHub issue]: https://github.com/adamsamec/VoiceToggle/issues
