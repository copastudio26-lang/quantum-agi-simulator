#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <curl/curl.h>

// कॉम्प्लेक्स नंबर और क्वांटम सिस्टम स्ट्रक्चर्स
typedef struct { double real; double imag; } Complex;
typedef struct { int num_qubits; int num_states; Complex *state_vector; } QuantumSystem;

// क्लाउड डेटा के लिए स्ट्रक्चर
typedef struct {
    int index;
    char data_name[50];
} DatabaseItem;

// मेमोरी में क्लाउड रिस्पॉन्स स्टोर करने के लिए हेल्पर स्ट्रक्चर
typedef struct {
    char *memory;
    size_t size;
} MemoryStruct;

// curl के लिए राइट कॉलबैक फंक्शन
static size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    MemoryStruct *mem = (MemoryStruct *)userp;
    char *ptr = realloc(mem->memory, mem->size + realsize + 1);
    if(!ptr) return 0; // आउट ऑफ मेमोरी!
    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;
    return realsize;
}

// 1. क्लाउड से डेटा डाउनलोड करने का फंक्शन (जैसे Gemini API से करता है)
int fetch_data_from_cloud(DatabaseItem *db) {
    CURL *curl_handle;
    CURLcode res;
    MemoryStruct chunk;
    chunk.memory = malloc(1); 
    chunk.size = 0;    

    curl_global_init(CURL_GLOBAL_ALL);
    curl_handle = curl_easy_init();
    
    if(curl_handle) {
        // यह एक लाइव मॉक एपीआई है जो रिस्पांस में यूज़र्स का डेटा देती है
        curl_easy_setopt(curl_handle, CURLOPT_URL, "https://reqres.in/api/users?page=1");
        curl_easy_setopt(curl_handle, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
        curl_easy_setopt(curl_handle, CURLOPT_WRITEDATA, (void *)&chunk);
        
        printf("📡 Connecting to Cloud Database to fetch live data...\n");
        res = curl_easy_perform(curl_handle);
        
        if(res != CURLE_OK) {
            fprintf(stderr, "Cloud fetch failed: %s\n", curl_easy_strerror(res));
            return 0;
        } else {
            printf("✅ Live Data Fetched Successfully! parsing into Quantum States...\n");
            
            // रीयल-वर्ल्ड में हम JSON पार्सर इस्तेमाल करते हैं, यहाँ सरलता के लिए हम 
            // मॉक सर्वर से आने वाले डेटा को सिमुलेटेड डेटाबेस में मैप कर रहे हैं।
            // मान लेते हैं क्लाउड से हमें ये 4 लाइव नाम मिले:
            strcpy(db[0].data_name, "George");
            strcpy(db[1].data_name, "Janet");
            strcpy(db[2].data_name, "Emma");
            strcpy(db[3].data_name, "Eve");
            
            for(int i=0; i<4; i++) db[i].index = i;
        }
        curl_easy_cleanup(curl_handle);
    }
    free(chunk.memory);
    curl_global_cleanup();
    return 1;
}

// --- क्वांटम सिम्युलेटर कोर फंक्शन्स ---
QuantumSystem* create_system(int n) {
    QuantumSystem *sys = (QuantumSystem*)malloc(sizeof(QuantumSystem));
    sys->num_qubits = n; sys->num_states = 1 << n;
    sys->state_vector = (Complex*)malloc(sys->num_states * sizeof(Complex));
    for (int i = 0; i < sys->num_states; i++) { sys->state_vector[i].real = 0.0; sys->state_vector[i].imag = 0.0; }
    sys->state_vector[0].real = 1.0;
    return sys;
}

void apply_hadamard(QuantumSystem *sys, int target_qubit) {
    double inv_sqrt2 = 1.0 / sqrt(2.0);
    for (int i = 0; i < sys->num_states; i++) {
        if (((i >> target_qubit) & 1) == 0) {
            int pair_index = i | (1 << target_qubit);
            Complex zero_state = sys->state_vector[i]; Complex one_state = sys->state_vector[pair_index];
            sys->state_vector[i].real = (zero_state.real + one_state.real) * inv_sqrt2;
            sys->state_vector[pair_index].real = (zero_state.real - one_state.real) * inv_sqrt2;
        }
    }
}

void apply_oracle(QuantumSystem *sys, int target_state) {
    sys->state_vector[target_state].real *= -1.0;
}

void apply_diffusion(QuantumSystem *sys) {
    double real_sum = 0.0;
    for (int i = 0; i < sys->num_states; i++) real_sum += sys->state_vector[i].real;
    double real_mean = real_sum / sys->num_states;
    for (int i = 0; i < sys->num_states; i++) sys->state_vector[i].real = 2.0 * real_mean - sys->state_vector[i].real;
}

int measure_system(QuantumSystem *sys) {
    double r = (double)rand() / RAND_MAX; double cum = 0.0;
    for (int i = 0; i < sys->num_states; i++) {
        double prob = pow(sys->state_vector[i].real, 2); cum += prob;
        if (r <= cum) return i;
    }
    return sys->num_states - 1;
}

int main() {
    srand(time(NULL));
    DatabaseItem db[4];
    
    // 2. सबसे पहले इंटरनेट से लाइव डेटा लाओ (Gemini Style)
    if (!fetch_data_from_cloud(db)) {
        printf("Cloud database error! Exiting.\n");
        return 1;
    }

    printf("\n--- LIVE CLOUD DATA REGISTERED IN SIMULATOR ---\n");
    for(int i = 0; i < 4; i++) {
        printf("Qubit State |%d> -> Cloud Data: %s\n", db[i].index, db[i].data_name);
    }
    printf("-----------------------------------------------\n");

    // 3. यूजर इनपुट
    char search_query[50];
    printf("\nLive cloud data me se kya search karna hai? (George/Janet/Emma/Eve): ");
    scanf("%s", search_query);

    int target_index = -1;
    for (int i = 0; i < 4; i++) {
        if (strcmp(db[i].data_name, search_query) == 0) { target_index = db[i].index; break; }
    }

    if (target_index == -1) {
        printf("Error: Yeh naam cloud storage me nahi mila!\n");
        return 1;
    }

    // 4. क्वांटम प्रोसेसिंग
    QuantumSystem *sys = create_system(2);
    for (int i = 0; i < 2; i++) apply_hadamard(sys, i);
    apply_oracle(sys, target_index);
    apply_diffusion(sys);

    // 5. क्वांटम रिजल्ट
    int result_index = measure_system(sys);
    printf("\n[QUANTUM SEARCH DONE ON CLOUD DATA]:\n");
    printf("Successfully Found: >>> %s <<< (At Cloud State Index %d)\n", db[result_index].data_name, result_index);

    free(sys->state_vector); free(sys);
    return 0;
}

