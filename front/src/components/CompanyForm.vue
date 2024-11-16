<script setup>
  import { endpoints } from '@/utils/backendEndpoints';

  const api = inject('api');

  const showForm = ref(false);
  const companyName = ref('');
  const valid = ref(false);
  const isEditing = ref(false);
  let editingCompanyId = null;

  const rules = {
    required: (value) => !!value || 'Required.',
  };

  const emit = defineEmits(['companyCreated', 'companyUpdated']);

  const openForm = (company = null) => {
    // Opens the company form for creating or editing a company.
    if (company) {
      // If a company object is provided, populate the form fields for editing.
      companyName.value = company.company_name; 
      isEditing.value = true;
      editingCompanyId = company.company_id;
    } else {
      // Otherwise, reset the form fields for creating a new company.
      companyName.value = '';
      isEditing.value = false;
      editingCompanyId = null;
    }
    showForm.value = true;
  };

  const closeForm = () => {
    // Closes the company form.
    showForm.value = false;
  };

  const submitForm = async () => {
    // Submits the company form to create or update a company.
    if (valid.value) {
      try {
        const method = isEditing.value ? 'put' : 'post';
        const url = isEditing.value 
        ? `${endpoints.companies.update}`
        : endpoints.companies.create;

        const data = isEditing.value ? 
          {
            company_id: editingCompanyId,
            company_name: companyName.value,
          } :
          {
            company_name: companyName.value,
          }
        const response = await api({
        method,
        url,
        headers: {
          'Content-Type': 'application/json',
        },
        data: data
      });

      if ((response.status === 200) || (response.status === 201)) {
          if (isEditing.value) {
            emit('companyUpdated');
          } else {
            emit('companyCreated');
          }
          closeForm();
        } else {
          console.error('Failed to submit company form');
        }
      } catch (error) {
        console.error('Error submitting form:', error);
      }
    }
  };

  defineExpose({
    openForm,
  });

</script>

<template>
  <div>
    <VBtn @click="openForm()" color="primary">
      + Company
    </VBtn>

    <VDialog v-model="showForm" persistent max-width="600px">
      <VCard>
        <VCardTitle>
          <span class="headline">{{ isEditing ? 'Edit Company' : 'Register a New Company' }}</span>
        </VCardTitle>

        <VCardText>
          <VForm ref="form" v-model="valid" lazy-validation>
            <VTextField
              v-model="companyName"
              label="Company Name"
              :rules="[rules.required]"
              required
            ></VTextField>
          </VForm>
        </VCardText>

        <VCardActions>
          <VSpacer></VSpacer>
          <VBtn color="secondary" text @click="closeForm">Cancel</VBtn>
          <VBtn color="primary" text @click="submitForm">Submit</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </div>
</template>

<style scoped>
  .headline {
    font-weight: bold;
  }
</style>
