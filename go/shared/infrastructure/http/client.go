package http

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/systentandobr/toolkit/go/shared/infrastructure/config"
)

// Client representa um cliente HTTP
type Client struct {
	client  *http.Client
	baseURL string
	headers map[string]string
}

// ClientOption representa uma opção para configurar o cliente HTTP
type ClientOption func(*Client)

// WithTimeout define o timeout do cliente HTTP
func WithTimeout(timeout time.Duration) ClientOption {
	return func(c *Client) {
		c.client.Timeout = timeout
	}
}

// WithBaseURL define a URL base para as requisições
func WithBaseURL(baseURL string) ClientOption {
	return func(c *Client) {
		c.baseURL = baseURL
	}
}

// WithHeader adiciona um header às requisições
func WithHeader(key, value string) ClientOption {
	return func(c *Client) {
		c.headers[key] = value
	}
}

// NewClient cria um novo cliente HTTP
func NewClient(options ...ClientOption) *Client {
	cfg := config.Get()

	client := &Client{
		client: &http.Client{
			Timeout: cfg.Timeout,
		},
		headers: make(map[string]string),
	}

	// Aplica as opções
	for _, option := range options {
		option(client)
	}

	// Adiciona headers padrão se não foram definidos
	if _, ok := client.headers["Content-Type"]; !ok {
		client.headers["Content-Type"] = "application/json"
	}

	return client
}

// buildURL constrói a URL completa para a requisição
func (c *Client) buildURL(path string) string {
	if c.baseURL == "" {
		return path
	}
	return fmt.Sprintf("%s/%s", c.baseURL, path)
}

// applyHeaders aplica os headers configurados à requisição
func (c *Client) applyHeaders(req *http.Request) {
	for key, value := range c.headers {
		req.Header.Set(key, value)
	}
}

// Get realiza uma requisição GET
func (c *Client) Get(ctx context.Context, path string, result interface{}) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.buildURL(path), nil)
	if err != nil {
		return err
	}

	c.applyHeaders(req)
	return c.do(req, result)
}

// Post realiza uma requisição POST
func (c *Client) Post(ctx context.Context, path string, body interface{}, result interface{}) error {
	jsonBody, err := json.Marshal(body)
	if err != nil {
		return err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.buildURL(path), bytes.NewBuffer(jsonBody))
	if err != nil {
		return err
	}

	c.applyHeaders(req)
	return c.do(req, result)
}

// Put realiza uma requisição PUT
func (c *Client) Put(ctx context.Context, path string, body interface{}, result interface{}) error {
	jsonBody, err := json.Marshal(body)
	if err != nil {
		return err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPut, c.buildURL(path), bytes.NewBuffer(jsonBody))
	if err != nil {
		return err
	}

	c.applyHeaders(req)
	return c.do(req, result)
}

// Delete realiza uma requisição DELETE
func (c *Client) Delete(ctx context.Context, path string, result interface{}) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodDelete, c.buildURL(path), nil)
	if err != nil {
		return err
	}

	c.applyHeaders(req)
	return c.do(req, result)
}

// do executa a requisição HTTP e processa a resposta
func (c *Client) do(req *http.Request, result interface{}) error {
	resp, err := c.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Lê o corpo da resposta
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	// Verifica o status code
	if resp.StatusCode >= 400 {
		return fmt.Errorf("request failed with status code %d: %s", resp.StatusCode, string(body))
	}

	// Se não há resultado esperado, retorna
	if result == nil {
		return nil
	}

	// Decodifica o resultado
	if err := json.Unmarshal(body, result); err != nil {
		return err
	}

	return nil
}
