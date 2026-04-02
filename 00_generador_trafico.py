import pandas as pd
import numpy as np
import random
import uuid
from datetime import datetime, timedelta

def generate_synthetic_data(n_records=5000):
    print(f"Generando {n_records} registros de tráfico sintético...")
    
    # Parámetros base
    variantes = ['A', 'B'] # A = Control, B = Tratamiento
    dispositivos = ['mobile', 'desktop', 'tablet']
    fuentes = ['email', 'social_media', 'organic', 'paid_search']
    
    # Tasas de conversión base (Variant B is intentionally better to test hypothesis later)
    # Control (A) ~ 8% conversion, Treatment (B) ~ 12% conversion
    base_conversion_rates = {'A': 0.08, 'B': 0.12}

    data = []
    
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(n_records):
        lead_id = str(uuid.uuid4())
        
        # Generar timestamp aleatorio en los últimos 30 días
        random_days = random.randint(0, 30)
        random_seconds = random.randint(0, 86400)
        timestamp = start_date + timedelta(days=random_days, seconds=random_seconds)
        
        # Asignación de variante (~50/50)
        variante = random.choice(variantes)
        
        # Otros atributos
        dispositivo = random.choices(dispositivos, weights=[0.6, 0.3, 0.1])[0]
        fuente = random.choice(fuentes)
        
        # Decidir si convierte o no basado en la variante
        conversion_prob = base_conversion_rates[variante]
        
        # Añadir un poco de ruido basado en el dispositivo (mobile convierte un poco menos aquí)
        if dispositivo == 'mobile':
            conversion_prob -= 0.01
            
        conversion = 1 if random.random() < conversion_prob else 0
        
        data.append({
            'lead_id': lead_id,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'variante': variante,
            'dispositivo': dispositivo,
            'fuente': fuente,
            'conversion': conversion
        })
        
    df = pd.DataFrame(data)
    
    # ==========================================
    # INTRODUCIR SESGOS Y DATOS SUCIOS INTENCIONALES
    # Para poner a prueba las habilidades de Data Cleaning
    # ==========================================
    print("Introduciendo anomalías y datos sucios...")
    
    # 1. Duplicar algunos leads (aprox 2%)
    num_duplicates = int(n_records * 0.02)
    duplicates = df.sample(n=num_duplicates, random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # 2. Valores nulos en dispositivo (aprox 3%)
    null_indices = df.sample(frac=0.03).index
    df.loc[null_indices, 'dispositivo'] = np.nan
    
    # 3. Variantes inválidas (e.g., 'C' o 'test')
    invalid_variant_indices = df.sample(frac=0.01).index
    df.loc[invalid_variant_indices, 'variante'] = random.choices(['C', 'test', 'A_old'], k=len(invalid_variant_indices))
    
    # 4. Timestamps futuros o muy antiguos
    outlier_time_indices = df.sample(frac=0.01).index
    # Fechas en el año 1999 o en el año 2050
    df.loc[outlier_time_indices, 'timestamp'] = [
        (datetime.now() + timedelta(days=365*10)).strftime('%Y-%m-%d %H:%M:%S') if random.random() > 0.5 
        else '1999-01-01 12:00:00' 
        for _ in range(len(outlier_time_indices))
    ]
    
    # Mezclar el dataframe para no tener los duplicados al final
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Guardar a CSV
    output_filename = 'raw_leads.csv'
    df.to_csv(output_filename, index=False)
    
    print(f"Generación completa. Dataset guardado en '{output_filename}'.")
    print(df.head())
    print("\nResumen inicial de variantes (contando los sucios):")
    print(df['variante'].value_counts(dropna=False))

if __name__ == "__main__":
    generate_synthetic_data(n_records=5000)
