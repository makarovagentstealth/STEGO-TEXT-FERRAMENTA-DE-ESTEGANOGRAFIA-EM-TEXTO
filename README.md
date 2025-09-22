Stego Text - Ferramenta de Esteganografia em Texto

https://img.shields.io/badge/Python-3.6%2B-blue.svg
https://img.shields.io/badge/License-MIT-green.svg

Uma ferramenta avançada de esteganografia que esconde dados secretos em texto comum usando caracteres Unicode de largura zero, tornando a mensagem invisível a olho nu.

✨ Características

· 🔒 Codificação Invisível: Usa caracteres zero-width Unicode (\u200B e \u200C)
· 🎭 Canal Visual Opcional: Marcadores Markdown em negrito para sinalização visual
· 📦 Compressão: Suporte a compressão zlib para payloads maiores
· 📊 Header Robusto: Header de 40 bits com comprimento e flags
· 🔄 Codificação Densa: Distribui bits eficientemente por caracteres não-espaço
· 📁 Suporte a Arquivos: Embeda tanto texto quanto arquivos binários

🚀 Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd stego-text

# Ou apenas baixe o script
wget https://raw.githubusercontent.com/seu-usuario/stego-text/main/stego_text.py

# Torne executável (opcional)
chmod +x stego_text.py
```

📋 Pré-requisitos

· Python 3.6 ou superior
· Nenhuma dependência externa necessária

🎯 Como Usar

Codificar uma Mensagem

```bash
# Método básico
python stego_text.py encode \
    --host-text "Este é um texto normal para esconder a mensagem" \
    --text "Mensagem secreta aqui" \
    --outfile texto_codificado.txt

# Com arquivos
python stego_text.py encode \
    --host-file documento.txt \
    --infile arquivo_secreto.zip \
    --outfile stego.txt \
    --compress \
    --bold
```

Decodificar uma Mensagem

```bash
# De arquivo
python stego_text.py decode \
    --infile texto_codificado.txt \
    --outfile mensagem_recuperada.txt

# Direto do texto
python stego_text.py decode \
    --text "$(cat texto_codificado.txt)"
```

⚙️ Opções de Comando

Comando encode

Opção Descrição Exemplo
--host-file Arquivo com texto hospedeiro --host-file texto.txt
--host-text Texto hospedeiro direto --host-text "Meu texto"
--infile Arquivo payload binário --infile secret.jpg
--text Texto payload direto --text "segredo"
--outfile Arquivo de saída --outfile stego.txt
--bold Adicionar marcadores em negrito --bold
--compress Comprimir payload --compress

Comando decode

Opção Descrição Exemplo
--infile Arquivo com texto codificado --infile stego.txt
--text Texto codificado direto --text "texto com segredo"
--outfile Arquivo para output binário --outfile recovered.bin

🧠 Exemplos Práticos

1. Esconder Mensagem em Texto

```bash
python stego_text.py encode \
    --host-text "O relatório trimestral mostra crescimento consistente nos principais indicadores de desempenho." \
    --text "Reunião secreta às 15h na sala 42B" \
    --bold \
    --outfile relatorio.txt
```

2. Esconder Arquivo Binário

```bash
python stego_text.py encode \
    --host-file artigo.txt \
    --infile chave_privada.pem \
    --compress \
    --outfile artigo_com_chave.txt
```

3. Decodificar e Ver Conteúdo

```bash
python stego_text.py decode --infile relatorio.txt
```

🔍 Como Funciona

Técnica Zero-Width

· \u200B (Zero Width Space) = bit 0
· \u200C (Zero Width Non-Joiner) = bit 1

Header Structure

```
[32 bits: comprimento do payload] + [8 bits: flags] = 40 bits total
```

Processo de Codificação

1. Converte payload para bits
2. Adiciona header com metadados
3. Distribui bits entre caracteres não-espaço
4. (Opcional) Adiciona marcadores em negrito

⚠️ Limitações e Considerações

Capacidade

· Texto Hospedeiro: Precisa ter caracteres suficientes não-espaço
· Payload Máximo: ~4GB (limitado pelo header de 32 bits)

Compatibilidade

· Editores de Texto: Alguns editores podem remover caracteres zero-width
· Plataformas: Sistemas podem normalizar Unicode diferentemente
· Formatos: Melhor resultados com arquivos de texto simples (.txt)

Boas Práticas

```bash
# ✅ Use arquivos texto simples
# ✅ Mantenha o texto original intacto
# ✅ Teste a decodificação após codificar
# ✅ Use --compress para payloads textuais
# ❌ Evite editores que normalizam Unicode
```

🐛 Solução de Problemas

Erro Comum: "no header found"

```bash
# Causas possíveis:
# - Texto foi editado após codificação
# - Caracteres zero-width foram removidos
# - Texto hospedeiro muito curto

# Solução: Use texto hospedeiro mais longo
python stego_text.py encode --host-text "$(cat long_text.txt)" --text "msg" --outfile output.txt
```

Verificar se a Codificação Funcionou

```bash
# Verifique se há caracteres zero-width
python -c "print(repr(open('stego.txt').read()))" | grep -E "200B|200C"

# Conte caracteres especiais
python -c "text = open('stego.txt').read(); print(f'Zero-width chars: {text.count(chr(0x200B)) + text.count(chr(0x200C))}')"
```

📊 Comparação de Técnicas

Técnica Invisível Capacidade Robustez
Zero-Width ✅ Alta ✅ Alta ⚠️ Média
Negrito Markdown ❌ Visível ✅ Alta ✅ Alta
Combinação ✅ Média ✅ Alta ✅ Alta

🛠️ Desenvolvimento

Estrutura do Código

```python
stego_text.py
├── encode_dense()      # Codificação principal
├── decode_dense()      # Decodificação principal
├── bytes_to_bits()     # Conversão bytes→bits
├── bits_to_bytes()     # Conversão bits→bytes
├── cli_encode()        # CLI para codificar
└── cli_decode()        # CLI para decodificar
```

Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

📝 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para detalhes.

⚡ Dicas Rápidas

```bash
# Codificação rápida
alias stego-encode='python stego_text.py encode'
alias stego-decode='python stego_text.py decode'

# Exemplo de uso rápido
stego-encode --host-text "Texto normal" --text "segredo" --bold
```

🔗 Links Úteis

· Unicode Zero-Width Characters
· Esteganografia Textual
· Python Unicode Handling

---

⚠️ Aviso: Use esta ferramenta apenas para fins legítimos e éticos. Não use para atividades ilegais ou maliciosas.

___________________________________________________________________###__________________________

https://renan21002200.wixsite.com/renansantoscyberseo

https://counterintelligencecoursescybernetics.wordpress.com/

https://cyberwarfarecounterintelligence.wordpress.com/

https://cyberaptsecurity.wordpress.com/

https://darkstrikaptevilcorpcounterintelligency.wordpress.com/

https://safehousessecurity.wordpress.com/

post completo no nosso website tbm: https://darkstrikaptevilcorpcounterintelligency.wordpress.com/2025/09/22/stego-text-ferramenta-de-esteganografia-em-texto/
