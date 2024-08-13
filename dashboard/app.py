import streamlit as st
import streamlit_shadcn_ui as ui

st.set_page_config(layout="wide")

def main():
    # col1, col2, col3 = st.columns(3)
    # col1.metric("Temperature", "70 °F", "1.2 °F")
    # col2.metric("Wind", "9 mph", "-8%")
    # col3.metric("Humidity", "86%", "4%")

    cols = st.columns(3)

    with cols[0]:
        ui.metric_card(
            title="Temperature",
            content="70 °F",
            description="+ 1.2 °F",
            key="card1",
        )

    with cols[1]:
        ui.metric_card(
            title="Wind",
            content="9 mph",
            description="-8%",
            key="card2",
        )

    with cols[2]:
        ui.metric_card(
            title="Humidity",
            content="86%",
            description="4%",
            key="card3",
        )



if __name__ == "__main__":
    main()