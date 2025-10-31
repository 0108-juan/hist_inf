import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""
if 'story_created' not in st.session_state:
    st.session_state.story_created = False

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración de la página
st.set_page_config(
    page_title='Tablero Inteligente - IA Creativa',
    layout='wide',
    page_icon="🎨",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem !important;
        color: #6a11cb;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.4rem !important;
        color: #4a5568;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 15px 15px 0 0;
        margin: 2rem 0 0 0;
        font-size: 1.3rem;
        font-weight: 600;
    }
    .analysis-content {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0 0 15px 15px;
        margin: 0 0 2rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .story-content {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0 0 15px 15px;
        margin: 0 0 2rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .canvas-container {
        border: 3px solid #e2e8f0;
        border-radius: 15px;
        padding: 10px;
        background: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }
    .stButton button {
        background: linear-gradient(45deg, #6a11cb, #2575fc);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(106, 17, 203, 0.4);
    }
    .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 10px;
    }
    .api-key-input {
        background: #f7fafc;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #6a11cb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .instructions-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">🎨 Tablero Inteligente - IA Creativa</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Dibuja tu boceto y descubre lo que la IA puede interpretar</h2>', unsafe_allow_html=True)

# Layout principal
col1, col2 = st.columns([1, 1])

with col1:
    # Panel de dibujo con marco unificado
    st.markdown('<div class="section-header">🖌️ Panel de Dibujo</div>', unsafe_allow_html=True)
    
    # Controles en tarjeta
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        stroke_width = st.slider(
            '**Grosor del pincel** ✏️',
            min_value=1,
            max_value=30,
            value=5,
            help="Ajusta el grosor del trazo para tu dibujo"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Canvas con contenedor estilizado
    st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=350,
        width=500,
        drawing_mode="freedraw",
        key="canvas",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input de API Key con marco unificado
    st.markdown('<div class="section-header">🔑 Configuración API</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="api-key-input">', unsafe_allow_html=True)
        ke = st.text_input(
            '**Ingresa tu Clave de OpenAI**',
            type="password",
            placeholder="sk-...",
            help="Necesitas una API key válida de OpenAI para usar esta aplicación"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Botón de análisis
    if canvas_result.image_data is not None and ke:
        analyze_button = st.button(
            "🔍 Analizar Boceto con IA",
            type="primary",
            use_container_width=True
        )
    else:
        analyze_button = st.button(
            "🔍 Analizar Boceto con IA",
            type="primary",
            use_container_width=True,
            disabled=True
        )

with col2:
    # Panel de resultados con marco unificado
    st.markdown('<div class="section-header">📊 Resultados e Interpretación</div>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_done:
        # Estado inicial - instrucciones
        with st.container():
            st.markdown('<div class="instructions-box">', unsafe_allow_html=True)
            st.markdown("""
            ### 🎯 Instrucciones:
            1. **Dibuja** tu boceto en el panel izquierdo
            2. **Ajusta** el grosor del pincel si es necesario
            3. **Ingresa** tu API key de OpenAI
            4. **Presiona** 'Analizar Boceto con IA'
            5. **¡Descubre** lo que la IA interpreta!
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Características de la aplicación
        with st.container():
            st.markdown("### ✨ Características")
            col_feat1, col_feat2 = st.columns(2)
            
            with col_feat1:
                st.markdown("""
                - 🎨 **Reconocimiento visual**
                - 📝 **Descripciones detalladas**
                - 🧠 **IA avanzada GPT-4**
                - ⚡ **Procesamiento rápido**
                """)
            
            with col_feat2:
                st.markdown("""
                - 📚 **Generación de historias**
                - 🎭 **Creatividad ilimitada**
                - 🔒 **Procesamiento seguro**
                - 🌍 **Multilenguaje**
                """)

    # Procesar análisis cuando se presiona el botón
    if canvas_result.image_data is not None and ke and analyze_button:
        os.environ['OPENAI_API_KEY'] = ke
        api_key = os.environ['OPENAI_API_KEY']

        with st.spinner("🔄 La IA está analizando tu boceto... Esto puede tomar unos segundos"):
            # Codificar imagen
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
            input_image.save('img.png')
            
            base64_image = encode_image_to_base64("img.png")
            st.session_state.base64_image = base64_image
                
            prompt_text = "Describe en español de manera detallada y creativa la imagen. Sé específico sobre lo que podría representar el dibujo."
        
            # Llamada a la API de OpenAI
            try:
                full_response = ""
                message_placeholder = st.empty()
                
                response = openai.chat.completions.create(
                  model="gpt-4o-mini",
                  messages=[
                    {
                       "role": "user",
                       "content": [
                         {"type": "text", "text": prompt_text},
                         {
                           "type": "image_url",
                           "image_url": {
                             "url": f"data:image/png;base64,{base64_image}",
                           },
                         },
                       ],
                      }
                    ],
                  max_tokens=500,
                )
                
                if response.choices[0].message.content is not None:
                    full_response = response.choices[0].message.content
                    st.markdown('<div class="analysis-content">', unsafe_allow_html=True)
                    st.markdown(f'**🎯 Análisis de la IA:**\n\n{full_response}')
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Guardar en session_state
                st.session_state.full_response = full_response
                st.session_state.analysis_done = True
                st.session_state.story_created = False
                
                if Expert == profile_imgenh:
                   st.session_state.mi_respuesta = response.choices[0].message.content
        
            except Exception as e:
                st.error(f"❌ Ocurrió un error: {e}")

    # Mostrar análisis previo si existe
    elif st.session_state.analysis_done:
        st.markdown('<div class="analysis-content">', unsafe_allow_html=True)
        st.markdown(f'**🎯 Análisis de la IA:**\n\n{st.session_state.full_response}')
        st.markdown('</div>', unsafe_allow_html=True)

    # Funcionalidad de crear historia si ya se hizo el análisis
    if st.session_state.analysis_done and not st.session_state.story_created:
        st.markdown('<div class="section-header">📚 Crear Historia Infantil</div>', unsafe_allow_html=True)
        
        if st.button("✨ Crear Historia Infantil", use_container_width=True):
            with st.spinner("🧚 Creando una historia mágica..."):
                story_prompt = f"""
                Basándote en esta descripción: '{st.session_state.full_response}', 
                crea una historia infantil breve, creativa y entretenida. 
                La historia debe ser apropiada para niños, con elementos mágicos 
                y un mensaje positivo. Incluye personajes interesantes y una trama sencilla.
                """
                
                try:
                    story_response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": story_prompt}],
                        max_tokens=600,
                    )
                    
                    st.markdown('<div class="story-content">', unsafe_allow_html=True)
                    st.markdown(f'**📖 Tu Historia Mágica:**\n\n{story_response.choices[0].message.content}')
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.session_state.story_created = True
                    
                except Exception as e:
                    st.error(f"❌ Error al crear la historia: {e}")

# Barra lateral mejorada
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown("## ℹ️ Acerca de")
    st.markdown("---")
    
    st.markdown("""
    ### 🎨 Tablero Inteligente
    
    Esta aplicación demuestra la capacidad avanzada de la **Inteligencia Artificial** 
    para interpretar y analizar bocetos dibujados a mano.
    
    **Tecnologías utilizadas:**
    - **OpenAI GPT-4 Vision** - Análisis visual
    - **Streamlit** - Interfaz de usuario
    - **PIL** - Procesamiento de imágenes
    """)
    
    st.markdown("---")
    
    st.markdown("### 🚀 Características Principales")
    st.markdown("""
    - ✏️ **Dibujo en tiempo real**
    - 🔍 **Análisis con IA**
    - 📖 **Generación de historias**
    - 🎯 **Interpretación creativa**
    - 💫 **Interfaz intuitiva**
    """)
    
    st.markdown("---")
    
    st.markdown("### 📝 Instrucciones Rápidas")
    st.markdown("""
    1. **Dibuja** en el panel principal
    2. **Configura** tu API key
    3. **Analiza** con IA
    4. **Crea** historias (opcional)
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔒 Seguridad")
    st.markdown("""
    Tu API key se utiliza solo para esta sesión y no se almacena permanentemente.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Advertencias para el usuario - CORREGIDO
if 'canvas_result' in locals() and canvas_result.image_data is not None and not ke:
    st.warning("🔑 **Por favor ingresa tu API key de OpenAI para analizar el boceto.**")

if 'canvas_result' in locals() and not canvas_result.image_data and ke:
    st.info("🎨 **¡Dibuja algo en el canvas para comenzar el análisis!**")
