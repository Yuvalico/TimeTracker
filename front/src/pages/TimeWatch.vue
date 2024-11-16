
<script setup>
import { endpoints } from '@/utils/backendEndpoints';
import { useAuthStore } from '@/store/auth';
import { ref, onMounted, computed } from 'vue';
import SimpleTable from '@/views/pages/tables/SimpleTable.vue'; 
import { VIcon } from 'vuetify/components/VIcon';
import timestampForm from '@/components/TimestampForm.vue'; 


const api = inject('api');
const authStore = useAuthStore();
const message = ref(''); 
const hasPunchIn = ref(false);
const punchOutDescription = ref('');
const selectedUser = ref(authStore.user.email);
const selectedUserData = ref([])
const userList = ref([])
const selectedCompany = ref(authStore.user.company_id);
const companyList = ref([])
const currentDate = ref(new Date());
const calendarData = ref([]);
const timestampFormRef = ref(null); 
const weekDays = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
const selectedYear = ref(new Date().getFullYear());
const selectedMonth = ref(new Date().getMonth());
const availableYears = ref([]); 
const availableMonths = ref([
  { title: 'January', value: 0 },
  { title: 'February', value: 1 },
  { title: 'March', value: 2 },
  { title: 'April', value: 3 },
  { title: 'May', value: 4 },
  { title: 'June', value: 5 },
  { title: 'July', value: 6 },
  { title: 'August', value: 7 },
  { title: 'September', value: 8 },
  { title: 'October', value: 9 },
  { title: 'November', value: 10 },
  { title: 'December', value: 11 },
]);

const calendarHeaders = ref([
  { text: 'Sun', value: 'sunday' },
  { text: 'Mon', value: 'monday' },
  { text: 'Tue', value: 'tuesday' },
  { text: 'Wed', value: 'wednesday' },
  { text: 'Thu', value: 'thursday' },
  { text: 'Fri', value: 'friday'   
 },
  { text: 'Sat', value: 'saturday'   
 },
]);

const editEntry = (event) => {
  // Opens the timestamp form with the provided event data for editing.
  console.log("Editing event: ", event);
  timestampFormRef.value.openForm(event);
};

async function checkPunchInStatus() {
  // Checks if the current user has an active punch-in timestamp.
  try {
    const response = await api.post(`${endpoints.timestamps.punchInStatus}`, {
      user_email: authStore.user.email
    });
    hasPunchIn.value = response.data.has_punch_in;
  } catch (error) {
    console.error('Error checking punch-in status:', error);
  }
};

async function punchIn() {
  // Creates a new punch-in timestamp for the current user.
  try {
    const response = await api.post(`${endpoints.timestamps.create}`, {
      user_email: authStore.user.email,
      punch_type: 0,  
      reporting_type: "work",
      detail: null
    });
    message.value = 'Punched in successfully';
    hasPunchIn.value = true;
    updateCalendar();
  } catch (error) {
    console.error('Error punching in:', error);
  }
};

async function punchOut() {
  // Updates the latest punch-in timestamp with punch-out information.
  try {
    const response = await api.put(`${endpoints.timestamps.punchOut}`, {
      user_email: authStore.user.email,
      entered_by: authStore.user.email,
      reporting_type: "work",
      detail: punchOutDescription.value
    });
    message.value = response.data.message;
    hasPunchIn.value = false;
    updateCalendar();
    punchOutDescription.value = '';
  } catch (error) {
    if (error.response && error.response.data.action_required === 'manual_punch_in') {
      message.value = 'No punch-in found for today. Please manually add a punch-in entry.';
    } else {
      console.error('Error punching out:', error);
    }
  }
};

async function deleteEntry(event) {
  // Deletes a timestamp entry after user confirmation.
  try {
    if (confirm('Are you sure you want to delete this entry?')) { 
      const response = await api.delete(`${endpoints.timestamps.delete}/${event.id}`);
      console.log(response.data.message); 
      updateCalendar(); 
    }
  } catch (error) {
    console.error('Error deleting time entry:', error);
    if (error.response) {
      message.value = 'Error deleting entry: ' + error.response.data.error; 
    } else {
      message.value = 'Error deleting entry.';
    }
  }
}

const addEntry = (dayData) => {
  // Opens the timestamp form to add a new entry for the specified day.
  const initialDate = new Date(selectedYear.value, selectedMonth.value, dayData.day);
  timestampFormRef.value.openForm(initialDate); 
};

function calculateDailyTotal(events) {
  // Calculates the total time in seconds for a day, considering different reporting types.
  let totalTime = 0;
  events.forEach(event => {
    if (event.reporting_type === 'paidoff') {
      totalTime += 8 * 3600; 
    } else {
      totalTime += event.total_time; 
    }
  });
  return totalTime
}

function calculateDailyTotalString(events) {
  // Calculates the total time for a day and formats it as HH:MM.
  const total = calculateDailyTotal(events)
  return formatTimeFromSeconds(total); 
}

const totalTimeWorkedThisMonth = computed(() => {
  // Calculates the total time worked in the current month, formatted as HH:MM.
  let totalTime = 0;
  calendarData.value.forEach(week => {
    Object.values(week).forEach(day => {
      if (day.events) {
        totalTime += calculateDailyTotal(day.events); 
      }
    });
  });
  return formatTimeFromSeconds(totalTime);
});

function formatTimeFromSeconds(totalSeconds) {
  // Formats time from seconds to HH:MM.
  const hours = Math.round(totalSeconds / 3600).toString().padStart(2, '0');
  const minutes = Math.round((totalSeconds % 3600) / 60).toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

function buildCalendar(currentDate) {
  // Builds the calendar data for the given date.
  const firstDay = (new Date(currentDate.getFullYear(), currentDate.getMonth())).getDay();
  const daysInMonth = 32 - new Date(currentDate.getFullYear(), currentDate.getMonth(), 32).getDate();
  const days = [];
  let dayCounter = 1;

  for (let i = 0; i < 6; i++) {
    let isEmptyWeek = true;
    const week = {};

    for (let j = 0; j < 7; j++) {
      const dayName = weekDays[j];
      if (i === 0 && j < firstDay) {
        week[dayName] = '';
      } else if (dayCounter > daysInMonth) {
        week[dayName] = '';
      } else {
        week[dayName] = {
          day: dayCounter,
          events: [],
        };
        dayCounter++;
        isEmptyWeek = false;
      }
    }
    if (!isEmptyWeek) {
      days.push(week);
    }
  }
  calendarData.value = days;
}

async function fetchTimeEntries(currentDate) {
  // Fetches time entries for the selected user and month.
  try {
    const start = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const end = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

    const response = await api.get(`${endpoints.timestamps.getRange}/${selectedUser.value}`, {
      params: {
        start_date: start.toISOString(),
        end_date: end.toISOString(),
      },
    });

    const events = response.data.map(entry => ({
      id: entry.uuid,
      inTime: new Date(entry.punch_in_timestamp),
      outTime: entry.punch_out_timestamp ? new Date(entry.punch_out_timestamp) : null, 
      description: entry.detail? entry.detail : null,
      total_time: entry.total_work_time,
      punchType: entry.punch_type,
      reporting_type: entry.reporting_type
    }));

    calendarData.value.forEach((week, weekIndex) => {
      Object.keys(week).forEach(dayName => {
        const dayData = week[dayName];
        if (dayData && dayData.day) {
          const eventsForDay = events.filter(event => {
            return (
              event.inTime.getDate() === dayData.day &&
              event.inTime.getMonth() === currentDate.getMonth() &&
              event.inTime.getFullYear() === currentDate.getFullYear()
            );
          });

          eventsForDay.sort((a, b) => a.inTime - b.inTime); 
          dayData.events = eventsForDay;
        }
      });
    });
  } catch (error) {
    console.error('Error fetching time entries:', error);
  }
}

function formatTime(date) {
  // Formats a date object to HH:MM string, returns '?' if date is null.
  if (!date) return '?';
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

const updateCalendar = () => {
  // Updates the calendar data and view.
  console.log("updating calendar");
  currentDate.value = new Date(selectedYear.value, selectedMonth.value);
  console.log(currentDate.value);
  buildCalendar(currentDate.value); 
  fetchTimeEntries(currentDate.value);
  checkPunchInStatus()
};

async function fetchCompanies() {
  // Fetches the list of companies.
  try {
    const response = await api.get(`${endpoints.companies.getActive}`);
    companyList.value = response.data; 
    console.log('Companies fetched:', companyList.value);
  } catch (error) {
    console.error('Error fetching companies:', error);
  }
}

async function fetchUsers() {
  // Fetches the list of users for the selected company.
  try {
    const userResponse = await api.get(`${endpoints.companies.getCompanyUsers}/${selectedCompany.value}/users`);
    userList.value = userResponse.data.map(user => ({
      "company_id": user.company_id,
      "company_name": user.company_name,
      "email": user.email,
      "is_active": user.is_active,
      "mobile_phone": user.mobile_phone,
      "permission": user.permission,
      "role": user.role,
      "salary": user.salary,
      "work_capacity": user.work_capacity,
      "weekend_choice": user.weekend_choice,
      "full_name": `${user.first_name} ${user.last_name}` 
    }));
    console.log('Users fetched:', userList.value);
  } catch (error) {
    console.error('Error fetching users:', error);
  }
}

async function fetchSelf() {
  // Fetches the current user's data.
  try {
    const userResponse = await api.get(`${endpoints.users.getByEmail}/${authStore.user.email}`);
    const user = userResponse.data; 

    selectedUserData.value = {
      "company_id": user.company_id,
      "company_name": user.company_name,
      "email": user.email,
      "is_active": user.is_active,
      "mobile_phone": user.mobile_phone,
      "permission": user.permission,
      "role": user.role,
      "salary": user.salary,
      "work_capacity": user.work_capacity,
      "weekend_choice": user.weekend_choice,
      "full_name": `${user.first_name} ${user.last_name}` 
    };

    console.log('User fetched:', selectedUserData.value);
  } catch (error) {
    console.error('Error fetching user:', error);
  }
}

function hasDayOff(dayData) {
  // Checks if the given day has any 'paidoff' or 'unpaidoff' events.
  if (dayData && dayData.events) {
    return dayData.events.some(event => 
      event.reporting_type === 'unpaidoff' || event.reporting_type === 'paidoff'
    );
  }
  return false;
}

const hasCurrentDayOff = computed(() => {
  // Checks if the current day is a day off for the selected user.
  const today = new Date();
  const day = today.getDate();
  const dayIndex = today.getDay();
  const dayName = weekDays[dayIndex];

  return isDayOff(day, dayName);
});

function isDayOff(day, dayName){  
  // Checks if the given day is a day off, considering weekend choice and calendar events.
  if (!selectedUserData.value.weekend_choice)
    return false;
  
  if (isWeekend(dayName)){
    return true;
  }  
  const currentDayData = calendarData.value.flatMap(week => Object.values(week))
    .find(dayData => dayData.day === day);

    return hasDayOff(currentDayData)
}

function isWeekend(dayName){
  // Checks if the given day name is a weekend day for the selected user.
  if(!selectedUserData.value.weekend_choice)
    return false;
  const weekendDays = selectedUserData.value.weekend_choice.split(',');
  const isDayOff = weekendDays.some(day => day.toLowerCase() === dayName.toLowerCase());
    return isDayOff
}

onMounted(async () => {
  // Initializes the component when it's mounted.
  checkPunchInStatus();
  buildCalendar(currentDate.value);
  await fetchTimeEntries(currentDate.value);
  const thisYear = new Date().getFullYear();
  for (let i = thisYear - 5; i <= thisYear + 5; i++) {
    availableYears.value.push(i);
  }
  fetchSelf()
  if (authStore.isNetAdmin || authStore.isEmployer){
    fetchCompanies();
    fetchUsers();
  }
});

watch(selectedMonth, (newMonth) => {
  // Watches for changes in the selected month and updates the calendar.
  console.log('Selected month:', newMonth);
  updateCalendar(); 
});

watch(selectedYear, (newYear) => {
  // Watches for changes in the selected year and updates the calendar.
  console.log('Selected year:', newYear);
  updateCalendar(); 
});

watch(selectedCompany, (newCompany) => {
  // Watches for changes in the selected company and fetches the users for that company.
  console.log('Selected company:', newCompany);
  fetchUsers().then(() => { 
    selectedUser.value = ''; 
  });
});

watch(selectedUser, (newUser) => {
  // Watches for changes in the selected user and updates the calendar accordingly.
  console.log('Selected User:', newUser);
  if (newUser != ''){

    selectedUserData.value = userList.value.find(user => user.email === selectedUser.value);
    updateCalendar();
  }
});

</script>

<template>
  <div>
    <h2>Time Watch</h2>

    <!-- Punch In Punch Out Buttons -->
    <div v-if="selectedUser === authStore.user.email" class="punch-buttons">
      <VBtn @click="punchIn" :disabled="hasPunchIn || hasCurrentDayOff" color="primary" class="punch-button">Punch In</VBtn>
      <div class="punch-out-group">
        <VBtn @click="punchOut" :disabled="!hasPunchIn || hasCurrentDayOff" color="primary" class="punch-button">Punch Out</VBtn>
        <VTextarea
        v-if="hasPunchIn"
        v-model="punchOutDescription"
        label="Task Description"
        placeholder="Enter task description"
        class="description-field"
        auto-grow
        rows="1" 
        />
      </div>
    </div>
    <div v-if="hasCurrentDayOff && selectedUser === authStore.user.email" class="day-off-message">
      Day Off - Cannot Punch In/Out
    </div>
    <div v-if="message">
      <VAlert
        type="warning"
        dismissible
        @click:close="() => { console.log('Clicked'); message = '' }"
        style="z-index: 10"
      >
        {{ message }}
    </VAlert>
    </div>
    <br>

    <!-- User Info and selection -->
    <div class="user-info"> 
        <div class="info-item full-width"> 
          <span class="label">Company:</span>
          <VSelect
          v-if="authStore.isNetAdmin"
          v-model="selectedCompany"
          :items="companyList"
          item-title="company_name"
          item-value="company_id"
        ></VSelect>
        <span v-else class="value">{{ authStore.user.company_name }}</span> 
      </div>
      
      <div class="info-item full-width">
        <span class="label">User:</span>
        <VSelect
          v-if="authStore.isNetAdmin || authStore.isEmployer" 
          :items="userList"
          item-title="full_name"
          item-value="email"
          v-model="selectedUser"
        ></VSelect>
        <span v-else class="value">{{ authStore.user.f_name }} {{ authStore.user.l_name }}</span> 
      </div>

       <VRow no-gutters>
        <VCol cols="6" sm="6" md="6" lg="6"> 
          <div class="info-item">
            <span class="label">Email:</span>
            <span class="value">{{ selectedUser }}</span>
          </div>
          <div class="info-item">
            <span class="label">Role:</span>
            <span class="value">{{ selectedUserData.role }}</span>
          </div>
          <div class="info-item">
            <span class="label">Total time worked in {{ selectedMonth + 1 }}/{{ selectedYear }}:</span>
            <span class="value">{{ totalTimeWorkedThisMonth }} Hours</span>
          </div>
        </VCol>
        <VCol cols="6" sm="6" md="6" lg="6"> 
          <div class="info-item">
            <span class="label">Phone:</span>
            <span class="value">{{ selectedUserData.mobile_phone }}</span>
          </div>
          <div class="info-item">
            <span class="label">Salary:</span>
            <span class="value">{{ selectedUserData.salary }} USD</span>
          </div>
          <div class="info-item">
            <span class="label">Work Capacity:</span>
            <span class="value">{{ formatTimeFromSeconds(selectedUserData.work_capacity * 3600) }} Hours</span>
          </div>
         
        </VCol>
      </VRow>
    </div>

    <br>
    <div class="calendar-controls"> 
      <VSelect
        v-model="selectedYear"
        :items="availableYears"
        label="Year"
      ></VSelect>

      <VSelect 
        v-model="selectedMonth"
        :items="availableMonths"
        label="Month"
        item-text="title"
        item-value="value"
      ></VSelect>
    </div>

    <!-- Calendar Table -->
    <SimpleTable :headers="calendarHeaders" :items="calendarData">
      <template v-for="dayName in weekDays" :key="dayName" v-slot:[`item.${dayName}`]="{ item }">
        <div class="calendar-cell"
        :style="{ backgroundColor: isWeekend(dayName) && item[dayName]?.day ? '#d3d3d3 ' : 'inherit' }"> 
          <div v-if="item[dayName]?.day" class="day-number-frame">
            <span class="day-number">{{ item[dayName].day }}</span>
          </div>
          <IconBtn v-if="item[dayName]?.day && !isDayOff(item[dayName].day, dayName)" class="add-entry-button" @click="addEntry(item[dayName])"> 
            <VIcon icon="ri-add-circle-fill" color="primary" size="18" /> 
          </IconBtn>
          <span class="total-time" v-if="item[dayName]?.events?.length">
            Total: {{ calculateDailyTotalString(item[dayName].events) }}
          </span>
          <span class="weekend" v-if="isWeekend(dayName)  && item[dayName]?.day">
            <strong>Weekend!</strong>
          </span>
          <div v-if="item[dayName]?.events?.length" class="event-list">
            <ul>
              <li v-for="event in item[dayName].events" :key="event.id">
                <VTooltip location="top">  
                  <template v-slot:activator="{ props }">
                    <span v-if="event.reporting_type === 'work'" v-bind="props">
                      {{ formatTime(event.inTime) }} - {{ formatTime(event.outTime) }}
                    </span>
                    <span v-if="event.reporting_type === 'unpaidoff'" v-bind="props">
                      <strong>Unpaid Day Off</strong>
                    </span>
                    <span v-if="event.reporting_type === 'paidoff'" v-bind="props">
                      <strong>Paid Day Off</strong>
                    </span>
                  </template>
                  <span>{{ event.description }}</span>
                </VTooltip>
                <IconBtn @click="editEntry(event)"> 
                  <VIcon icon="ri-edit-line" size="18" /> 
                </IconBtn>
                <IconBtn @click="deleteEntry(event)">
                  <VIcon icon="ri-delete-bin-line" size="18" /> 
                </IconBtn>
              </li>
            </ul>
          </div>
        </div>
        <timestampForm ref="timestampFormRef" 
                 @timestampCreated="updateCalendar"  
                 @timestampUpdated="updateCalendar"
                 :selectedUser="selectedUser" /> 
      </template>
    </SimpleTable>
  </div>
</template>


<style scoped>
.punch-buttons {
  display: flex;
  align-items: flex-end; 
}

.punch-out-group {
  display: flex;
  align-items: flex-end; 
  margin-left: 15px; 
}

.punch-button {
  margin: 15px 0; 
  height: 60px;
  font-size: 22px;
  width: 150px;
}

.description-field {
  margin: 15px; 
  height: 60px;
  width: 300px; 
  align-self: flex-end; 
}

.description-field textarea { 
  resize: none; 
}

.user-info {
  background-color: "inherit";
  border: 1px solid #ccc;  
  padding: 20px;           
  border-radius: 8px;      
  margin-bottom: 20px;      
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); 
}

.info-item {
  display: flex;           
  align-items: center;   
  margin-bottom: 15px;     
}

.info-item .label {
  font-weight: bold;       
  font-size: 18px;        
  margin-right: 10px;      
}

.info-item .value {
  font-size: 20px;        
}

.user-info .v-row {  
  margin-bottom: 0px; 
}
  
.user-info .v-col { 
  padding: 0 10px; 
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

th, td {
  border: 1px solid #ccc;
  text-align: center;
  padding: 10px;
  height: 120px; 
  position: relative;
}

.calendar-cell {
  position: relative;
  display: flex;
  padding-top: 30px;
  height: 100%;
  flex-direction: column;
  align-items: center;
}

.calendar-cell::before {
  content: '';
  display: block;
  padding-top: 25%; 
}

.day-number-frame {
  position: absolute;
  top: 5px; 
  left: 50%;
  transform: translateX(-50%);
  background-color: #e2c6f5; 
  border-radius: 50%;
  width: 25px; 
  height: 25px; 
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.day-number {
  font-size: 1em;
  font-weight: bold;
  color: #333; 
}

.event-list {
  white-space: nowrap;
  overflow: hidden; 
  text-overflow: ellipsis;
  order: -1;
  margin-top: 10px; 
  width: 100%;
  text-align: left;
}

.event-list ul {
  white-space: nowrap;
  overflow: hidden; 
  text-overflow: ellipsis;
  padding-left: 0px;
  list-style-type:disc;
  text-align: left;
  list-style-position: inside;
}

.event-list li {
  align-items: center;
  justify-content: space-between;
  white-space: nowrap;
  overflow: hidden; 
  text-overflow: ellipsis;
  font-size: 1em;
  margin-top: 5px;
  text-align: left
  
}

.calendar-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.total-time {
    white-space: nowrap;
    overflow: hidden; 
    text-overflow: ellipsis;
    font-weight: bold;
    position: absolute; 
    bottom: 5px;
    left: 50%;
    transform: translateX(-50%);
    padding: 0 5px;
    font-size: 1em; 
  }

.add-entry-button {
  position: absolute;
  top: 0px; 
  right: 5px; 
}
  
.event-description {
  display: block;  
  font-size: 0.8em;
  margin-top: 5px;
}

.day-off-message {
  color: red; 
  font-weight: bold;
  margin-bottom: 10px; 
  font-size: 1.2em;
}
.weekend{
  color-scheme:"primary";
}

</style>