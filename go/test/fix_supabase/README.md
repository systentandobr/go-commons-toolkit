# Correção para o Erro de Conexão com PostgreSQL

Este diretório contém scripts para corrigir o erro de conexão com o PostgreSQL:
```
dial tcp: lookup localhost:5432: no such host
```

## Problema Identificado

O erro ocorre porque a função `getHost` no cliente Supabase está extraindo incorretamente a string `localhost:5432` da URI `postgresql://localhost:5432` e tentando usá-la como hostname. 

Um host não deve conter dois pontos (`:`) e porta - isso é interpretado como uma tentativa de resolver DNS para o hostname `localhost:5432`, que não existe.

## Solução

A correção consiste em:

1. Separar corretamente o host e a porta na URI
2. Substituir 'localhost' por '127.0.0.1' para evitar problemas de resolução DNS
3. Usar parâmetros de conexão explícitos na string de conexão PostgreSQL

## Arquivos

- `client_fixed.go`: Versão corrigida do client.go para o Supabase
- `test_connections.go`: Ferramenta para testar diferentes tipos de conexão

## Como usar

1. Execute o script de teste para diagnosticar o problema:
   ```
   cd /home/marcelio/developing/systentando/toolkit/go/test/fix_supabase
   go run test_connections.go
   ```

2. Substitua o arquivo client.go original pela versão corrigida:
   ```
   cp client_fixed.go ../../shared/infrastructure/persistence/supabase/client.go
   ```

3. Alternativamente, apenas mude a configuração:
   ```
   # No arquivo .env
   SUPABASE_URI=postgresql://127.0.0.1:5432
   ```

## Explicação da Correção

O problema principal está na função `getHost` que faz:

```go
// Implementação atual
func getHost(uri string) string {
    if len(uri) > 13 {
        return uri[13:] // Retorna "localhost:5432" para "postgresql://localhost:5432"
    }
    return "localhost:5432"
}
```

A correção implementa uma função `extractHostPort` que:

1. Remove corretamente o prefixo "postgresql://"
2. Divide a string por ":" para separar host e porta
3. Substitui "localhost" por "127.0.0.1" para evitar problemas DNS
4. Usa parâmetros explícitos host= e port= na string de conexão

Isso garante que o PostgreSQL receba parâmetros de conexão corretos.
