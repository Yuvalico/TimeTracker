<script setup>
  import { ref, onMounted } from 'vue';
  import { useAuthStore } from '@/store/auth';
  import { useRouter } from 'vue-router';
  import SimpleTable from '@/views/pages/tables/SimpleTable.vue';
  import UserForm from '@/components/UserForm.vue';
  import CompanyForm from '@/components/CompanyForm.vue';
  import { endpoints } from '@/utils/backendEndpoints';

  const api = inject('api');

  const router = useRouter();
  const authStore = useAuthStore();
  console.log(authStore);


  if (authStore.isEmployee) {
    router.push('/timewatch'); 
  }


  const users = ref([]);
  const companies = ref([]);
  const companiesWithAdmins = ref([]);
  const selectedCompany = ref("Filter Users by Company"); 
  const showRemoveUserDialog = ref(false);
  const userToRemove = ref(null);
  const employmentEndDate = ref(new Date()); 
  const today = new Date().toISOString().slice(0, 10); 
  const showReactivateUserDialog = ref(false);
  const userToReactivate = ref(null);
  const showDeletedUsers = ref(false);
  const userFormRef = ref(null); 
  const companyFormRef = ref(null); 


  const userHeaders = computed(() => {
    const headers  = [
      { text: 'Name', value: 'fullName' },
      { text: 'Mobile Phone', value: 'mobile_phone' },
      { text: 'Email', value: 'email' },
      { text: 'Company Name', value: 'company_name' },
      { text: 'Role', value: 'role' },
      { text: 'Salary', value: 'salary' },
      { text: 'Work Capacity', value: 'work_capacity' },
      { text: 'Employment Start', value: 'employment_start' },
      { text: 'Weekend Choice', value: 'weekend_choice' },
      { text: 'Permission', value: 'permission' },
    ];
    if (authStore.isNetAdmin) {
        headers.push({ text: '', value: 'actions', align: 'center', sortable: false });
      }
      return headers;
  });

  const companyHeaders = [
    { text: 'Company Name', value: 'companyName' },
    { text: 'Admin User', value: 'adminUser' },
    { text: '', value: 'actions', align: 'center', sortable: false },
  ];

  const companyOptions = computed(() => {
    // Computes the options for the company filter dropdown.
    return ['No Filter'].concat(companies.value.map(company => company.company_name));
  });

  const filteredUsers = computed(() => {
    // Computes the list of users to display, filtered by the selected company if applicable.
    console.log("Filtering users by company:", selectedCompany.value);
    if (authStore.isNetAdmin && selectedCompany.value !== "Filter Users by Company" && selectedCompany.value !== "No Filter") { // Check if a company is actually selected
      return users.value.filter(user => user.company_name === selectedCompany.value);
    } else {
      return users.value; 
    }
  });

  watch(() => users.value, (newUsers) => {
    // Watches for changes in the users list and fetches companies.
    console.log('users.value changed:', newUsers);
    fetchCompanies();
  });

  watch(() => showDeletedUsers.value, (newvalue) => {
    // Watches for changes in the showDeletedUsers flag and fetches users accordingly.
    console.log('showDeletedUsers.value changed:', newvalue);
    fetchUsers()
  });


  const reactivateUser = (user) => {
    // Opens the reactivate user dialog with the selected user.
    userToReactivate.value = user;
    showReactivateUserDialog.value = true;
  };

  const cancelReactivateUser = () => {
    // Closes the reactivate user dialog and resets the selected user.
    showReactivateUserDialog.value = false;
    userToReactivate.value = null;
  };

  const confirmReactivateUser = async () => {
    // Reactivates the selected user.
    try {
      const method = 'put' 
      const url = endpoints.users.reactivate
        
      const response = await api({
        method,
        url,
        headers: {
          'Content-Type': 'application/json',
        },
        data: {
          user_email: userToReactivate.value.email,
        },
      });
      if (response.status === 200) {
        console.log('User reactivated successfully');
        fetchUsers();
      } else {
        console.error('Failed to reactivate user');
      }
    } catch (error) {
      console.error('Error reactivating user:', error);
    } finally {
      showReactivateUserDialog.value = false;
      userToReactivate.value = null;
      fetchUsers();
    }
  };

  async function fetchUsers() {
    // Fetches the list of users, either active or inactive based on showDeletedUsers flag.
    try {
      let userResponse;
      if (!showDeletedUsers.value){
        userResponse = await api.get(`${endpoints.users.getActive}`);
      }
      else{
        userResponse = await api.get(`${endpoints.users.getNotActive}`);
      }
        console.log(userResponse.data)
        users.value = (await userResponse.data).map(user => ({
          ...user,
          fullName: `${user.first_name} ${user.last_name}`,
          actions: {
            edit: () => editUser(user),
            remove: () => removeUser(user),
          },
        }));

      console.log('Users fetched:', users.value);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  }

  async function fetchCompanies() {
    // Fetches the list of companies and their admins.
    try {
      const companyResponse =  await api.get(`${endpoints.companies.getActive}`); 
      companies.value = (await companyResponse.data).map(company => ({
        ...company,
        companyName: company.company_name,
        actions: {
          edit: () => editCompany(company),
          remove: () => removeCompany(company),
        },
      }));

      companiesWithAdmins.value = companies.value.map(company => ({
        companyName: company.company_name,
        adminUser: getAdminUser(company.company_id),
        actions: company.actions,
      }));
    } catch (error) {
      console.error('Error fetching companies:', error);
    }
  }

  function getAdminUser(companyID) {
    // Finds the admin user for the given company ID.
    console.log('Looking for admin in companyID:', companyID);
    
    const adminUser = users.value.find(user => {
      return user.company_id === companyID && (user.permission === 1 || user.permission === 0);
    });

    console.log('Admin user found:', adminUser);
    return adminUser ? `${adminUser.first_name} ${adminUser.last_name}` : 'No Admin';
  }

  function editUser(user) {
    // Opens the user form for editing the given user.
    console.log("Editing user: ", user);
    userFormRef.value.openForm(user);
    fetchUsers();
  }

  const removeUser = (user) => {
    // Opens the remove user dialog with the selected user.
    userToRemove.value = user;
    showRemoveUserDialog.value = true;
  };

  const cancelRemoveUser = () => {
    // Closes the remove user dialog and resets the selected user and employment end date.
    showRemoveUserDialog.value = false;
    userToRemove.value = null;
    employmentEndDate.value = new Date();
  };

  const confirmRemoveUser = async () => {
    // Removes the selected user.
    try {
      const user = userToRemove.value;
      user.employment_end = employmentEndDate.value ? employmentEndDate.value.toISOString() : new Date().toISOString();

      const response = await api.put(`${endpoints.users.remove}/${user.email}`, user);

      if (response.status === 200) {
        console.log('User removed successfully');
        fetchUsers();
      } else {
        console.error('Failed to remove user');
      }
    } catch (error) {
      console.error('Error removing user:', error);
    } finally {
      showRemoveUserDialog.value = false;
      userToRemove.value = null;
      employmentEndDate.value = new Date();
      fetchUsers();
    }
  };

  function editCompany(company) {
    // Opens the company form for editing the given company.
    console.log("Editing company: ", company);
    companyFormRef.value.openForm(company);
    fetchCompanies();
  }

  function formatWeekendChoice(weekendChoice) {
    // Formats the weekend choice string for display.
    if (weekendChoice) {
      return weekendChoice.split(',').join(', '); 
    }
    return '';
  }

  function permission2str(value) {
    // Converts a permission value to its string representation.
    if (value == 0){
      return 'Net Admin';
    }
    else if(value == 1){
      return 'Employer';
    }
    else if(value == 2){
      return 'Employee';
    }
    else{
      return "Unknown"
    }
  }

  function formatDate(dateString) {
    // Formats a date string for display.
    if (dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric', weekday: 'short' };
      return new Date(dateString).toLocaleDateString('en-US', options);
    }
    return '';
  }

  const removeCompany = async (company) => {
    // Removes the given company.
    try {
      const response = await api.put(`${endpoints.companies.remove}/${company.company_id}`);

      if (response.status === 200) {
        console.log('Company removed successfully');
        fetchCompanies();
      } else {
        console.error('Failed to remove company');
      }
    } catch (error) {
      console.error('Error removing company:', error);
    }
  };

  onMounted(() => {
    // Fetches users and companies when the component is mounted.
    fetchUsers();
    if (authStore.isNetAdmin){
      fetchCompanies();
    }
  });

</script>

<template>
  <VRow>
    <VCol cols="12">
      <VCard>
        <VCardTitle class="d-flex justify-space-between align-center">
          <span>
            <span v-if="authStore.isEmployer">
              {{ authStore.user.company_name }} - 
            </span>
            <span>Users</span>
          </span>

          <div v-if="authStore.isNetAdmin" class="d-flex align-center"> 
            <VSwitch v-model="showDeletedUsers" :label="showDeletedUsers ? 'Show Active Users' : 'Show Inactive Users'" class="mr-4" /> 
            <VSelect
              v-model="selectedCompany"
              :items="companyOptions"
              label="Select Company"
              class="mr-4" 
            />
          </div>

          <UserForm v-if="authStore.isNetAdmin" ref="userFormRef" @userCreated="fetchUsers" @userUpdated="fetchUsers" />
        </VCardTitle>

        <SimpleTable :headers="userHeaders" :items="filteredUsers">
          <template v-slot:item.actions="{ item }">
            <div class="actions-col" v-if="authStore.isNetAdmin">
              <IconBtn
                v-if="!showDeletedUsers"
                icon="ri-edit-line"
                @click="item.actions.edit"
              />
              <IconBtn
                v-if="!showDeletedUsers"
                icon="ri-delete-bin-line"
                @click="item.actions.remove"
              />
              <VBtn 
                v-if="showDeletedUsers" 
                color="primary" 
                variant="outlined" 
                size="small" 
                @click="reactivateUser(item)">
                + Reactivate
              </VBtn>
            </div>
          </template>
          <template v-slot:item.employment_start="{ item }">
            {{ formatDate(item.employment_start) }} 
          </template>
          <template v-slot:item.weekend_choice="{ item }">
            {{ formatWeekendChoice(item.weekend_choice) }} 
          </template>
          <template v-slot:item.permission="{ item }">
            {{ permission2str(item.permission) }}
          </template>
        </SimpleTable>
      </VCard>
    </VCol>

    <VCol cols="12" class="mt-4" v-if="authStore.isNetAdmin"> 
      <VCard>
        <VCardTitle class="d-flex justify-space-between align-center">
          <span>Companies</span>
          <CompanyForm ref="companyFormRef" @companyCreated="fetchCompanies" @companyUpdated="fetchCompanies" />
        </VCardTitle>
        <SimpleTable :headers="companyHeaders" :items="companiesWithAdmins">
          <template v-slot:item.actions="{ item }">
            <div class="actions-col">
              <IconBtn
                icon="ri-edit-line"
                @click="item.actions.edit"
              />
              <IconBtn
                icon="ri-delete-bin-line"
                @click="item.actions.remove"
              />
            </div>
          </template>
          
        </SimpleTable>
      </VCard>
    </VCol>
    <VDialog v-model="showRemoveUserDialog" persistent max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="headline">Remove User</span>
        </VCardTitle>
        <VCardText>
          <div>
            <p v-if="userToRemove">Are you sure you want to remove <strong>{{ userToRemove.first_name }} {{userToRemove.first_name}}</strong>?</p> 
            <VDatePicker v-model="employmentEndDate" :value="today" /> 
          </div>
        </VCardText>
        <VCardActions>
          <VBtn color="secondary" variant="outlined" @click="cancelRemoveUser">Cancel</VBtn>
          <VBtn color="error" @click="confirmRemoveUser">Remove</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
    <VDialog v-model="showReactivateUserDialog" persistent max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="headline">Reactivate User</span>
        </VCardTitle>
        <VCardText>
          <div v-if="userToReactivate">
            <p>Are you sure you want to reactivate <strong>{{ userToReactivate.first_name }} {{ userToReactivate.last_name }}</strong>?</p> 
          </div>
        </VCardText>
        <VCardActions>
          <VBtn color="secondary" variant="outlined" @click="cancelReactivateUser">Cancel</VBtn>
          <VBtn color="success" @click="confirmReactivateUser">Reactivate</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </VRow>
</template>
