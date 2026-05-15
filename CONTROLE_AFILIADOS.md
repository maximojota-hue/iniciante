# Controle de Afiliados - Clube 3D Brasil

Lista sequencial simples dos produtos afiliados enviados pelo usuario.

## Como Usar

Quando o usuario enviar um produto, registrar:

1. Numero sequencial.
2. Nome curto.
3. Link afiliado.
4. Caminho da foto.
5. Status da foto.
6. Observacoes.

Em uma nova postagem, o usuario pode informar apenas o numero do afiliado, por exemplo:

```text
usar afiliado #3
```

Tambem pode enviar um produto novo com:

```text
nome curto + link afiliado + foto
```

Ou autorizar:

```text
criar sem afiliado
```

## Lista

| # | Nome curto | Link afiliado | Foto | Status | Observacoes |
|---:|---|---|---|---|---|
| 1 | A cadastrar | - | - | vazio | Proximo produto enviado pelo usuario deve substituir esta linha ou criar a linha #2. |

## Regra Para Posts

Antes de criar qualquer post, o Codex deve:

1. Dizer claramente sobre o que sera o post.
2. Perguntar se deve usar um afiliado cadastrado pelo numero.
3. Aceitar cadastro de um novo afiliado com nome curto, link e foto.
4. Aceitar a opcao `criar sem afiliado`.

Depois de usar um afiliado em post, registrar o numero dele tambem em `CONTROLE_POSTS.md`.
