<script setup>
  import { endpoints } from '@/utils/backendEndpoints';

  const api = inject('api');

  const emit = defineEmits(['userCreated', 'userUpdated']);

  const showForm = ref(false);
  const isEditing = ref(false); 
  const firstName = ref('');
  const lastName = ref('');
  const email = ref('');
  const mobile_phone = ref(null);
  const password = ref('');
  const selectedCompany = ref('');
  const role = ref('');
  const permission = ref(null);
  const salary = ref(null);
  const workCapacity = ref(null);
  const employmentStart = ref(null);
  const employmentEnd = ref(null);
  const selectedWeekDays = ref([]);
  const formValid = ref(false);
  const form = ref(null);
  const serverErrorMessage = ref(null); 

  const weekDays = ref([
    'Sunday', 
    'Monday', 
    'Tuesday', 
    'Wednesday', 
    'Thursday', 
    'Friday', 
    'Saturday'
  ]);
  const companies = ref([]); 

  const permissions = ref(['Net Admin', 'Employer', 'Employee']);
  const requiredRule = (value) => !!value || 'Required';
  const emailRule = (value) => /.+@.+\..+/.test(value) || 'E-mail must be valid';
  const mobilePhoneRule = (value) => /^\d{10}$/.test(value) || 'Mobile phone must be exactly 10 digits and only numbers';

  async function fetchCompanies() {
    // Fetches the list of active companies from the API.
    try {
      const response = await api.get(`${endpoints.companies.getActive}`);
      const data = await response.data;

      companies.value = data.map(company => company.company_name);
      
      console.log('Companies fetched:', companies.value);
    } catch (error) {
      console.error('Error fetching companies:', error);
    }
  }

  const validateForm = async () => {
    // Validates the user form and updates formValid reactive variable.
    if (form.value) {
      const validationResult = await form.value.validate();
      formValid.value = validationResult.valid;
    } else {
      formValid.value = false;
    }
  };

  const isFormValid = computed(() => formValid.value); // Computed property for form validity.


  watch(formValid, (newVal) => {
    // Watches for changes in form validity and logs the new state.
    console.log("Form validation state changed:", newVal);
  });

  watch(
    // Watch for changes in the form fields.
    // Trigger form validation when any of the watched values change.
    () => [firstName.value, lastName.value, email.value, selectedCompany.value, password.value, role.value, permission.value, employmentStart.value, salary.value, workCapacity.value, selectedWeekDays.value],
    () => validateForm()
  );

  onMounted(fetchCompanies); // Fetch companies when the component is mounted.

  function openForm(user = null) {
    // Opens the form for creating or editing a user.
    if (user) {
      // If user is provided, populate the form with user data for editing.
      isEditing.value = true;
      firstName.value = user.first_name;
      lastName.value = user.last_name;
      email.value = user.email;
      mobile_phone.value = user.mobile_phone;
      password.value = ''; 
      selectedCompany.value = user.company_name;
      role.value = user.role;
      permission.value = permissions.value[user.permission];
      salary.value = user.salary;
      workCapacity.value = user.work_capacity;
      employmentStart.value = user.employment_start ? new Date(user.employment_start) : null;
      employmentEnd.value = user.employment_end ? new Date(user.employment_end) : null;
      selectedWeekDays.value = user.weekend_choice ? user.weekend_choice.split(',') : []; 
    } else {
      // If no user is provided, reset the form for creating a new user.
      isEditing.value = false;
      resetForm();
    }
    showForm.value = true;
  }

  function resetForm() {
    // Resets the form fields and validation.
    firstName.value = '';
    lastName.value = '';
    email.value = '';
    mobile_phone.value = null;
    password.value = '';
    selectedCompany.value = '';
    role.value = '';
    permission.value = null;
    salary.value = null;
    workCapacity.value = null;
    employmentStart.value = null;
    employmentEnd.value = null;
    selectedWeekDays.value = [];
    if (form.value) {
      form.value.resetValidation();
    }
  }

  const submitForm = async () => {
    // Submits the form to create or update a user.
    serverErrorMessage.value = null;
    try {
      const method = isEditing.value ? 'put' : 'post';
      const url = isEditing.value
        ? `${endpoints.users.update}` 
        : endpoints.users.create;

      console.log({
        first_name: firstName.value,
        last_name: lastName.value,
        mobile_phone: mobile_phone.value,
        email: email.value,
        password: password.value, 
        company_name: selectedCompany.value,
        role: role.value,
        permission: permission.value,
        salary: salary.value,
        work_capacity: workCapacity.value,
        employment_start: employmentStart.value ? employmentStart.value.toISOString() : null,
        weekend_choice: selectedWeekDays.value.join(','), 
      });

      const response = await api({
        method,
        url,
        headers: {
          'Content-Type': 'application/json',
        },
        data: {
          first_name: firstName.value,
          last_name: lastName.value,
          mobile_phone: mobile_phone.value,
          email: email.value,
          password: password.value,
          company_name: selectedCompany.value,
          role: role.value,
          permission: {
            'Net Admin': 0,
            'Employer': 1,
            'Employee': 2
          }[permission.value],
          salary: salary.value,
          work_capacity: workCapacity.value,
          employment_start: employmentStart.value ? employmentStart.value.toISOString() : null,
          weekend_choice: selectedWeekDays.value.join(','), 
        },
      });

      if ((response.status === 200) || (response.status === 201)) {
        if (isEditing.value) {
          console.log('User updated successfully');
          emit('userUpdated');  
        } else {
          console.log('User created successfully');
          emit('userCreated');  
        }
        showForm.value = false; 
      } else {
        console.error('Failed to submit form');
        const errorData = await response.data;
        console.error('Error details:', errorData);
        serverErrorMessage.value = errorData.error || 'Unknown error';
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      serverErrorMessage.value = error.response.data.error ||'Network error or server unavailable';
    }
  };

  defineExpose({
    openForm,
  });
</script>

<template>
  <VBtn @click="openForm()" color="primary">
    + User
  </VBtn>

  <VDialog v-model="showForm" persistent max-width="600px">
    <VCard>
      <VCardTitle>
        <span class="headline">{{ isEditing ? 'Edit User' : 'Register a New User' }}</span>
      </VCardTitle>

      <VCardText>
        <VForm ref="form" @submit.prevent="submitForm">
          <VRow>
            <VCol cols="12">
              <VTextField
                v-model="firstName"
                prepend-inner-icon="ri-user-line"
                label="First Name"
                placeholder="John"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="lastName"
                prepend-inner-icon="ri-user-line"
                label="Last Name"
                placeholder="Doe"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="mobile_phone"
                prepend-inner-icon="ri-smartphone-line"
                label="Mobile Phone"
                placeholder="1 123 456 7890"
                type="number"
                :rules="[mobilePhoneRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="email"
                prepend-inner-icon="ri-mail-line"
                label="Email"
                type="email"
                placeholder="johndoe@example.com"
                :rules="[requiredRule, emailRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="password"
                prepend-inner-icon="ri-lock-line"
                label="Password"
                autocomplete="on"
                type="password"
                placeholder="············"
                :rules="isEditing ? [] : [requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VAutocomplete
                v-model="selectedCompany"
                :items="companies"
                label="Company Name"
                item-text="company_name"
                item-value="company_id"
                prepend-inner-icon="ri-building-line"
                placeholder="Select or Search Company"
                :rules="[requiredRule]"
              />
            </VCol>
            
            <VCol cols="12">
              <VDatePicker 
                v-model="employmentStart" 
                title="employement start date" 
                label="Employment Start" 
                :rules="[requiredRule]">
              </VDatePicker>
            </VCol>
  
            <VCol cols="12">
              <VTextField
                v-model="role"
                prepend-inner-icon="ri-briefcase-line"
                label="Role"
                placeholder="Developer"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VSelect
                v-model="permission"
                :items="permissions"
                label="Permission"
                item-text="text"
                item-value="value"
                prepend-inner-icon="ri-shield-line"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="salary"
                prepend-inner-icon="ri-money-dollar-circle-line"
                label="Salary"
                type="number"
                placeholder="50000"
                :rules="[requiredRule]"
              />
            </VCol>

            <VCol cols="12">
              <VTextField
                v-model="workCapacity"
                prepend-inner-icon="ri-time-line"
                label="Daily Work Capacity"
                type="number"
                placeholder="160"
                :rules="[requiredRule]"
              />
            </VCol>

            <p style="margin: 15px;"> <strong>Weekend Selection </strong> </p> 
            <VRow>
              <VCol cols="12">
                  <VCardText class="weekend-selection"> 
                    <VRow>
                      <VCol
                        v-for="day in weekDays"
                        :key="day"
                        cols="12"
                        md="6"
                      >
                        <VCheckbox v-model="selectedWeekDays" :label="day" :value="day" density="compact"></VCheckbox>
                      </VCol>
                    </VRow>
                  </VCardText>
              </VCol>
              </VRow>
              <div v-if="serverErrorMessage" class="server-error"> 
                {{ serverErrorMessage }}
              </div>
            <VCol cols="12" class="d-flex justify-end">
              <VBtn
                color="secondary"
                type="reset"
                variant="outlined"
                @click="showForm = false"
                class="me-2"
              >
                Cancel
              </VBtn>
              
              <VBtn
                type="submit"
                :disabled="!isFormValid"
              >
                {{ isEditing ? 'Update' : 'Submit' }}
              </VBtn>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>
  </VDialog>
</template>

<style scoped>
  .weekend-selection .v-field__label {
    position: absolute;
    top: -15px; 
    left: 0;
    font-size: 14px; 
    color: #000; 
  }

  .end-date-picker {
    padding-left: 16px; 
  }
  .server-error { 
    color: red;
    margin-top: 10px;
  }
</style>