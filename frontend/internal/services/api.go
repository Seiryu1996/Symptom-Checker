package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

type APIService struct {
	BaseURL    string
	HTTPClient *http.Client
}

func NewAPIService(baseURL string) *APIService {
	return &APIService{
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

type SymptomInput struct {
	Text     string `json:"text"`
	Severity *int   `json:"severity,omitempty"`
	Duration string `json:"duration,omitempty"`
	Location string `json:"location,omitempty"`
}

type SymptomResponse struct {
	ID       string   `json:"id"`
	Text     string   `json:"text"`
	Severity *int     `json:"severity"`
	Duration string   `json:"duration"`
	Location string   `json:"location"`
	Category string   `json:"category"`
	Keywords []string `json:"keywords"`
}

type DiagnosisInput struct {
	Symptoms      []string `json:"symptoms"`
	PatientAge    *int     `json:"patient_age,omitempty"`
	PatientGender string   `json:"patient_gender,omitempty"`
	Duration      string   `json:"duration,omitempty"`
	Severity      *int     `json:"severity,omitempty"`
}

type MedicalSpecialty struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Urgency     string `json:"urgency"`
}

type DiagnosisResult struct {
	PossibleConditions     []string           `json:"possible_conditions"`
	RecommendedSpecialties []MedicalSpecialty `json:"recommended_specialties"`
	UrgencyLevel           string             `json:"urgency_level"`
	Advice                 string             `json:"advice"`
	Confidence             float64            `json:"confidence"`
}

type Location struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	Address   string  `json:"address"`
}

type Hospital struct {
	ID          string     `json:"id"`
	Name        string     `json:"name"`
	Location    Location   `json:"location"`
	Phone       string     `json:"phone"`
	Specialties []string   `json:"specialties"`
	Distance    *float64   `json:"distance"`
	Rating      *float64   `json:"rating"`
	Website     string     `json:"website,omitempty"`
	Emergency   bool       `json:"emergency"`
}

type HospitalSearchParams struct {
	Specialties     []string  `json:"specialties"`
	UserLocation    *Location `json:"user_location,omitempty"`
	MaxDistance     *float64  `json:"max_distance,omitempty"`
	EmergencyOnly   bool      `json:"emergency_only"`
}

func (s *APIService) SubmitSymptom(input SymptomInput) (*SymptomResponse, error) {
	url := fmt.Sprintf("%s/api/v1/symptoms/input", s.BaseURL)
	
	jsonData, err := json.Marshal(input)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := s.HTTPClient.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to submit symptom: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	var result SymptomResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &result, nil
}

func (s *APIService) AnalyzeSymptoms(input DiagnosisInput) (*DiagnosisResult, error) {
	url := fmt.Sprintf("%s/api/v1/diagnosis/analyze", s.BaseURL)
	
	jsonData, err := json.Marshal(input)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := s.HTTPClient.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to analyze symptoms: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	var result DiagnosisResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &result, nil
}

func (s *APIService) SearchHospitals(params HospitalSearchParams) ([]Hospital, error) {
	url := fmt.Sprintf("%s/api/v1/hospitals/search", s.BaseURL)
	
	jsonData, err := json.Marshal(params)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := s.HTTPClient.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to search hospitals: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	var hospitals []Hospital
	if err := json.NewDecoder(resp.Body).Decode(&hospitals); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return hospitals, nil
}

func (s *APIService) GetSymptomCategories() (map[string]interface{}, error) {
	url := fmt.Sprintf("%s/api/v1/symptoms/categories", s.BaseURL)
	
	resp, err := s.HTTPClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to get symptom categories: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	var categories map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&categories); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return categories, nil
}

func (s *APIService) ProxyRequest(method, path string, body io.Reader) (*http.Response, error) {
	url := fmt.Sprintf("%s/api/v1%s", s.BaseURL, path)
	
	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	
	resp, err := s.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to proxy request: %w", err)
	}

	return resp, nil
}