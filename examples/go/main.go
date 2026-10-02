package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

func main() {
	if err := send(); err != nil {
		fmt.Fprintln(os.Stderr, "Send failed. Check variables, connectivity and intake credentials.")
		os.Exit(1)
	}
	fmt.Println("Event accepted. Confirm indexing in Kibana.")
}

func send() error {
	url, password := os.Getenv("LOGSTASH_URL"), os.Getenv("LOGSTASH_PASSWORD")
	if url == "" || password == "" {
		return fmt.Errorf("missing variables")
	}
	body, err := json.Marshal(map[string]interface{}{
		"message": "hello from Go", "service": "example-go", "level": "info",
		"attributes": map[string]string{"language": "go"},
	})
	if err != nil {
		return err
	}
	request, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return err
	}
	request.SetBasicAuth("shipper", password)
	request.Header.Set("Content-Type", "application/json")
	client := &http.Client{Timeout: 10 * time.Second,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}
	response, err := client.Do(request)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return fmt.Errorf("intake rejected event")
	}
	return nil
}
