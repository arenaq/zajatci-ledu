# Projekt Zajatci ledu – historie a podklady

## Původ

25. 10. 2026 vyfotil Petr v muzeu v norském Tromsø 19 panelů s úryvky deníku Gerrita de Veera
(*Waerachtighe beschryvinghe van drie seylagien*, Amsterdam 1598) v norštině, každý s rytinou a datem.
Z nich vznikl přepis s věrným českým překladem (lokálně `../denik_prepis_a_preklad.md`, mimo veřejný
repozitář) a z překladu scénář vyprávění v `_build/slides.json`.

## Panely, snímky a rytiny

Rytiny na panelech jsou totožné s tisky Rijksmusea; v prezentaci jsou použity skeny z Commons (CC0).
Fotky 16 a 17 byly nafocené v opačném pořadí, snímky jsou řazené podle data.

| Panel (foto `PXL_20261025_…`) | Datum | Snímek | Titulek | Rytina |
| --- | --- | --- | --- | --- |
| 1 (`145306584`) | 26. 8. 1596 | d01 | Sevřeni ledem | RP-P-OB-80.209 |
| 2 (`145311469`) | 28. 8. 1596 | d02 | Led zvedl loď | RP-P-OB-80.210 |
| 3 (`145316312`) | 11. 9. 1596 | d03 | Dřevo z moře | RP-P-OB-80.212 |
| 4 (`145321195`) | 15. 9. 1596 | d04 | Tři medvědi | RP-P-OB-80.211 |
| 5 (`145326047`) | 2. 10. 1596 | d05 | Stavba domu | RP-P-OB-80.213 |
| 6 (`145329430`) | 25. 10. 1596 | d06 | Medvědi u saní | RP-P-OB-80.214 |
| 7 (`145333854`) | 1. 12. 1596 | d07 | Zrádné teplo | RP-P-OB-80.215 |
| 8 (`145337806`) | 1. 12. 1596 | c01 (2. rytina) | Polární noc | RP-P-OB-80.216 |
| 9 (`145343109`) | 30.–31. 5. 1597 | d09 | Příprava člunů | RP-P-OB-80.218 |
| 10 (`145347383`) | 12. 6. 1597 | d10 | Cesta k moři | RP-P-OB-80.219 |
| 11 (`145352760`) | 13. 6. 1597 | d11 | Sbohem, Nová Země | RP-P-OB-80.220 |
| 12 (`145357295`) | 17.–20. 6. 1597 | d12 | Smrt Willema Barentse | RP-P-OB-80.221 |
| 13 (`145403207`) | 28.–29. 6. 1597 | d13 | Noční hlídka | RP-P-OB-80.222 |
| 14 (`145407501`) | 1. 7. 1597 | d14 | Kry pod nohama | RP-P-OB-80.223 |
| 15 (`145412107`) | 20. 7. 1597 | d15 | Volné moře | RP-P-OB-80.224 |
| 17 (`145421460`) | 28. 7. 1597 | d16 | Zase mezi lidmi | RP-P-OB-80.225 |
| 16 (`145417937`) | 16. 8. 1597 | d17 | Ruská lodja | RP-P-OB-80.226 |
| 18 (`145427131`) | 21. 8. 1597 | d18 | Shledání | RP-P-OB-80.227 |
| 19 (`145431565`) | 25. 8. 1597 | d19 | Kola | RP-P-OB-80.228 |

Doplněné snímky (úvod, kontext, epilog): s00 titulní mapa NG-1979-564-15, s01 dvě lodě RP-P-OB-80.205,
s02 Medvědí ostrov RP-P-OB-80.206 a Špicberky RP-P-OB-80.208, s03 Nová Země RP-P-OB-80.207,
c01 vnitřek chaty NG-1979-564-22, e01 mapa Nové Země RP-P-OB-80.229, e02 chata RP-P-OB-80.215,
z99 titulky RP-P-OB-80.205.

Poznámky k textu panelů:
- Panely 7 a 8 mají v muzeu stejný text. Snímek c01 proto vypráví o polární noci z historických zdrojů.
- Panel 17 píše „i fjor“ (loni) o setkání ve Vajgačské úžině; šlo o výpravu z roku 1595,
  ve vyprávění proto zní „už dříve“.

## Rozhodnutí

- **Formát:** webová prezentace místo PowerPointu, sdílitelná odkazem, běží sama po kliknutí na start.
- **Vyprávění:** panely jako deník v 1. osobě, úvod a epilog vypráví vypravěč. Na snímku jen datum a krátký
  titulek, celý text volitelně jako titulky (CC).
- **Kapitoly:** I · Na sever, II · Zima v ledu, III · Cesta domů, Epilog.
- **Hlas:** vyzkoušeny edge-tts (Vlasta, vícejazyčné Andrew/Florian), offline Windows Jakub a Piper Jirka.
  Uživatel chtěl rodilou češtinu; Azure Antonín by vyžadoval účet Azure. Zvolen ElevenLabs
  **Radan-Deep** (`Ds83HLxlalYdwK8IwqTu`), model **Eleven v4**, tarif Starter.
- **Vzhled:** jeden tmavý vzhled „polární noc“, písma Grenze Gotisch (titul), Alegreya a Alegreya Sans;
  rytiny v duotónu inkoust/pergamen.
- **Hosting:** GitHub Pages (veřejný repozitář), dříve i soukromý artefakt na claude.ai.

## Zdroje faktů pro úvod a epilog

- Elling Carlsen, rodák z Tromsø, našel chatu v roce 1871; nálezy jsou v Rijksmuseu a v Tromsø Museum:
  [Wikipedia](https://en.wikipedia.org/wiki/Elling_Carlsen), [Store norske leksikon](https://snl.no/Elling_Carlsen)
- Barentsova smrt 20. 6. 1597: [Royal Museums Greenwich](https://www.rmg.co.uk/collections/objects/rmgc-object-11851)
- Návrat slunce 24. 1. 1597, efekt Nové Země: [Wikipedia](https://en.wikipedia.org/wiki/Novaya_Zemlya_effect)
- Průběh třetí výpravy: [Atlas of Mutual Heritage](https://www.atlasofmutualheritage.nl/page/10599/third-expedition-to-the-arctic-led-by-barentsz-and-heemskerck)
- Rytiny: [Wikimedia Commons, Waerachtighe beschryvinghe](https://commons.wikimedia.org/wiki/Category:Waerachtighe_beschryvinghe_van_drie_seylagien)
  a sbírka Rijksmusea RP-P-OB-80.196–229

## Otevřené body

- Práva k norskému textu z panelů: před širším sdílením požádat muzeum o souhlas, nebo text přepsat
  podle volně dostupného anglického překladu de Veera (Hakluyt Society, 1876).
- API klíč ElevenLabs prošel chatem: po dokončení úprav ho v ElevenLabs smazat a vytvořit nový.
- Předplatné ElevenLabs Starter případně po měsíci zrušit.
