import streamlit as st
from datetime import datetime, time, date, timedelta

# ---------- Helper functions ----------
def convert_12hr_to_24hr(hour_12, minute, ampm):
    """Convert 12-hour format to 24-hour time object."""
    if ampm == "AM":
        if hour_12 == 12:
            hour_24 = 0
        else:
            hour_24 = hour_12
    else:  # PM
        if hour_12 == 12:
            hour_24 = 12
        else:
            hour_24 = hour_12 + 12
    return time(hour_24, minute)

def format_datetime_12hr(dt):
    """Format datetime to 'YYYY-MM-DD hh:MM AM/PM'."""
    return dt.strftime("%Y-%m-%d %I:%M %p")

def find_common_slots(stakeholders):
    """
    Find intersection of all datetime intervals across all stakeholders.
    stakeholders: list of dicts with 'name' and 'slots' (list of (start, end) datetime).
    Returns list of (start, end) datetime tuples common to all.
    """
    if not stakeholders:
        return []

    all_intervals = [s['slots'] for s in stakeholders]

    # Start with intervals of first person
    common = all_intervals[0]
    for person_intervals in all_intervals[1:]:
        new_common = []
        for c_start, c_end in common:
            for p_start, p_end in person_intervals:
                start = max(c_start, p_start)
                end = min(c_end, p_end)
                if start < end:
                    new_common.append((start, end))
        common = new_common
        if not common:
            break
    return common

# ---------- Session state ----------
if 'stakeholders' not in st.session_state:
    st.session_state.stakeholders = []  # each: {'name': str, 'slots': [(start, end), ...]}

if 'slot_count' not in st.session_state:
    st.session_state.slot_count = 1  # number of slot forms shown for current stakeholder

def add_stakeholder(name, slots):
    st.session_state.stakeholders.append({'name': name, 'slots': slots})

def reset_data():
    st.session_state.stakeholders = []
    st.session_state.slot_count = 1

# ---------- UI ----------
st.title("📅 Stakeholder Availability Overlap Finder")
st.markdown("Add each stakeholder and their available time slots (date and time in AM/PM). Then find times when everyone is free.")

# Input section
with st.expander("➕ Add a stakeholder", expanded=True):
    with st.form(key="stakeholder_form"):
        name = st.text_input("Name *", key="name_input")

        st.markdown("**Add time slots** (at least one):")
        slots = []  # will hold (start_datetime, end_datetime) for this stakeholder

        for i in range(st.session_state.slot_count):
            st.markdown(f"#### Slot {i+1}")
            col1, col2 = st.columns(2)

            with col1:
                slot_date = st.date_input(f"Date", value=date.today(), key=f"date_{i}")

                # Start time
                st.markdown("**Start time**")
                hr_start = st.number_input(
                    "Hour (1-12)", min_value=1, max_value=12, value=9, key=f"start_hr_{i}"
                )
                min_start = st.number_input(
                    "Minute", min_value=0, max_value=59, value=0, step=1, key=f"start_min_{i}"
                )
                ampm_start = st.selectbox(
                    "AM/PM", ["AM", "PM"], index=0, key=f"start_ampm_{i}"
                )

            with col2:
                # End time (same date assumed)
                st.markdown("**End time**")
                hr_end = st.number_input(
                    "Hour (1-12)", min_value=1, max_value=12, value=5, key=f"end_hr_{i}"   # <-- FIXED: value=5 (5 PM)
                )
                min_end = st.number_input(
                    "Minute", min_value=0, max_value=59, value=0, step=1, key=f"end_min_{i}"
                )
                ampm_end = st.selectbox(
                    "AM/PM", ["AM", "PM"], index=1, key=f"end_ampm_{i}"
                )

            # Convert to datetime
            start_time = convert_12hr_to_24hr(hr_start, min_start, ampm_start)
            end_time = convert_12hr_to_24hr(hr_end, min_end, ampm_end)
            start_dt = datetime.combine(slot_date, start_time)
            end_dt = datetime.combine(slot_date, end_time)

            if end_dt <= start_dt:
                st.warning(f"Slot {i+1}: End time must be after start time. Please adjust.")
            else:
                slots.append((start_dt, end_dt))

        # Buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            add_slot = st.form_submit_button("➕ Add another slot")
        with col2:
            submit = st.form_submit_button("✅ Add stakeholder")
        with col3:
            pass  # alignment

        if add_slot:
            st.session_state.slot_count += 1
            st.experimental_rerun()

        if submit:
            if name.strip() == "":
                st.error("Please enter a name.")
            elif not slots:
                st.error("Please add at least one valid time slot.")
            else:
                add_stakeholder(name.strip(), slots)
                st.success(f"Added {name}")
                # Reset slot count for next stakeholder
                st.session_state.slot_count = 1
                st.experimental_rerun()

# Display current stakeholders
if st.session_state.stakeholders:
    st.subheader("Current stakeholders")
    for i, s in enumerate(st.session_state.stakeholders):
        slot_str = ", ".join(
            [f"{format_datetime_12hr(start)} - {format_datetime_12hr(end)}" for start, end in s['slots']]
        )
        st.write(f"{i+1}. **{s['name']}**: {slot_str}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Find common free time"):
            common = find_common_slots(st.session_state.stakeholders)
            if common:
                st.subheader("✅ Common free time windows")
                for start, end in common:
                    st.write(f"{format_datetime_12hr(start)} → {format_datetime_12hr(end)}")
            else:
                st.warning("No common free time found.")
    with col2:
        if st.button("🗑️ Reset all"):
            reset_data()
            st.experimental_rerun()
else:
    st.info("No stakeholders added yet. Use the form above to add.")

# Footer
st.markdown("---")
st.markdown("Made with Streamlit. [GitHub repository](https://github.com/yourusername/stakeholder-availability)")
