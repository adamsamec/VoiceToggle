# VoiceToggle

## Introdução

O complemento VoiceToggle para o leitor de tela NVDA permite pré-configurar um número arbitrário de vozes em suas configurações, de modo que, posteriormente, você possa alternar rapidamente entre essas vozes em círculo a qualquer momento usando o simples atalho de teclado NVDA + Alt + V.

## Exemplo de uso

Digamos que você fale inglês e francês, então você pode adicionar duas vozes nas configurações do VoiceToggle, conforme descrito abaixo, uma com pronúncia em inglês e outra com pronúncia em francês. Posteriormente, você poderá alternar entre essas duas vozes usando apenas o atalho de teclado simples e confortável NVDA + Alt + V, em vez de mexer no anel de configurações do sintetizador NVDA, na caixa de diálogo de seleção do sintetizador NVDA ou na caixa de diálogo de configurações do NVDA na categoria Fala.

## Configuração das vozes

As vozes que podem ser alternadas com o VoiceToggle podem ser pré-configuradas seguindo estas etapas:

1. PressioneNVDA + N para abrir o menu NVDA.
2. Selecione o submenu "Preferências".
3. Selecione o item de menu "Configurações".
4. Navegue até a categoria “VoiceToggle”. A página de propriedades do VoiceToggle será aberta e a lista de vozes será preenchida somente com a voz atual.
5. Para adicionar outra voz à lista, abra a caixa de diálogo para adicionar uma nova voz usando o botão “Adicionar voz”.
6. Usando a primeira caixa de combinação, selecione primeiro o sintetizador desejado e, em seguida, usando a segunda caixa de combinação, selecione a voz desejada do sintetizador que deseja adicionar e pressione o botão “Adicionar". A voz recém-adicionada aparecerá na lista de vozes após o item atualmente selecionado na lista.
7. Não se esqueça de salvar as configurações que acabou de fazer pressionando o botão “OK” ou “Aplicar" no final da caixa de diálogo de configurações do NVDA.

## Lembrança de vozes para aplicativos individuais

Digamos que você queira navegar na Web em inglês, mas queira fazer anotações e todos os outros trabalhos em francês. Então, você pode fazer com que a última voz usada seja lembrada em determinados aplicativos. Por exemplo, quando você alterna para o Google Chrome, a voz muda automaticamente para a última voz usada nesse aplicativo, talvez em inglês. Então, quando você volta para outro aplicativo, por exemplo, para o Microsoft Word para fazer anotações em francês, a voz volta para a voz padrão em francês. Isso é possível graças ao recurso de perfis de configuração do NVDA.



Para configurar determinado aplicativo para que ele se lembre da última voz usada, siga estas etapas:

1. Alterne para esse aplicativo, por exemplo, para o Google Chrome.
2. PressioneNVDA + N para abrir o menu do NVDA.
3. Escolha o item de menu “Perfis de configuração".
4. Pressione o botão “Novo".
5. “Navegue até o botão de rádio rotulado como ”Ativação manual" no agrupamento ”Usar este perfil para" e alterne-o para ”Aplicativo atual" usando a tecla de seta para baixo.
6. Confirme a criação de um novo perfil de configuração usando o botão “OK”.



## Alteração do atalho de alternância de voz

O atalho de teclado padrão NVDA + Alt + V para alternância de voz pode ser alterado para outro atalho usando a caixa de diálogo “Gestos de entrada” da seguinte forma:

1. PressioneNVDA + N para abrir o menu do NVDA.
2. Selecione o submenu “Preferences” (Preferências).
3. Escolha o item de menu “Input gestures” (Gestos de entrada).
4. Digite “voice toggle” no campo de edição “Filtrar por”, incluindo o espaço entre as duas palavras.
5. Na árvore, navegue até o item “Alterna para a próxima voz" na categoria “Diversos".
6. Ative o botão ”Adicionar", pressione o atalho de teclado desejado e confirme com Enter.
7. Confirme a alteração usando o botão “OK”.



## Download

O VoiceToggle para NVDA está disponível na NVDA Add-on Store ou pode ser [baixado aqui][VoiceToggle-download].

## Registro de alterações

[O changelog pode ser visualizado aqui][changelog].

## Contato e feedback

Se tiver sugestões para aprimorar o VoiceToggle, problemas com sua funcionalidade ou outros comentários, envie-me um e-mail para [adam.samec@gmail.com](mailto:adam.samec@gmail.com)

## Licença

O VoiceToggle está disponível sob a Licença Pública Geral GNU versão 2.0.

[VoiceToggle-download]: https://files.adamsamec.cz/apps/nvda/VoiceToggle.nvda-addon
[VoiceToggle-download-nvda-2023-1]: https://files.adamsamec.cz/apps/nvda/VoiceToggle-1.4.1.nvda-addon
[changelog]: https://github.com/adamsamec/VoiceToggle/blob/main/Changelog.md