import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

st.title('Dashboard comparativo con Matplotlib y Plotly')   # Title

tips_df = sns.load_dataset('tips')  # Load dataset

# Sidebar filter
st.sidebar.header('Filtros')
selected_day = st.sidebar.selectbox('Selecciona un día:',
                                    tips_df['day'].unique().tolist(),
                                    index=None)

# Filter data
if selected_day:
    tips_df = tips_df[tips_df['day'] == selected_day]

# Show data table
st.subheader('Datos filtrados por día seleccionado')
st.dataframe(tips_df)

# Matplotlib chart
st.subheader('Gráfico con Matplotlib: Cuenta total vs Propina')

fig, ax = plt.subplots()

gender_list = tips_df['sex'].unique()
color_map = dict(zip(gender_list, ['#1f77b4', '#ff7f0e']))

for gender in gender_list:
    gender_data = tips_df[tips_df['sex'] == gender]
    ax.scatter(
        gender_data['total_bill'],
        gender_data['tip'],
        s=gender_data['size'] * 10,
        alpha=0.7,
        label=f'{gender}',
    )
ax.set_xlabel('Cuenta total')
ax.set_ylabel('Propina')
ax.set_title(f'Relación entre cuenta y propina ({selected_day})')
ax.legend(title='Sexo', title_fontsize=11, fontsize=10, loc='upper left')
st.pyplot(fig)

# Plotly chart
st.subheader('Gráfico con Plotly: Cuenta total vs Propina')

fig_plotly = px.scatter(
    tips_df,
    x='total_bill',
    y='tip',
    color='sex',
    color_discrete_sequence=['#1f77b4', '#ff7f0e'],
    size='size',
    size_max=10,
    title=f"Relación entre cuenta y propina ({selected_day if selected_day else  ' '})",
    labels={'total_bill': 'Cuenta total', 'tip': 'Propina', 'sex': 'Sexo', 'size': 'Tamaño del grupo'}
)
st.plotly_chart(fig_plotly)
