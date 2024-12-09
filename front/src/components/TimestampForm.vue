  <script setup>
    import { endpoints } from '@/utils/backendEndpoints';

    const api = inject('api');
    
    const emit = defineEmits(['timestampCreated', 'timestampUpdated']);
    const showForm = ref(false);
    const isEditing = ref(false);
    const entryId = ref(null); 
    const inTime = ref(null);
    const outTime = ref(null);
    const IsoInTime = ref(null);
    const IsoOutTime = ref(null);
    const description = ref(null);
    const reportingType = ref(null);
    const form = ref(null); 
    const formValid = ref(null); 
    const reportingTypeOptions = ref([
      { value: 'work', title: 'Work' },
      { value: 'unpaidoff', title: 'Unpaid Day Off' },
      { value: 'paidoff', title: 'Paid Day Off' },
    ]);
  
  const props = defineProps({
    selectedUser: {  
        type: String, 
        required: true, 
        },
    });

  const requiredRule = (value) => !!value || 'Required';
  
  const validateForm = async () => {
    // Validates the form and updates the formValid reactive variable.
    if (form.value) {
      const validationResult = await form.value.validate();
      formValid.value = validationResult.valid;
    } else {
      formValid.value = false;
    }
  };

  const isFormValid = computed(() => formValid.value);

  watch(formValid, (newVal) => {
    // Watches for changes in form validity and logs the new state.
    console.log("Form validation state changed:", newVal);
  });

  watch(
    // Watch for changes in these values.
    // Trigger form validation when any of the watched values change.
    () => [reportingType.value, inTime.value, outTime.value],
    () => validateForm()
  );

  function formatTime(dateObj) {
    // Formats a Date object or string to a time string in HH:MM format.
    if (!(dateObj instanceof Date)) {
        dateObj = new Date(dateObj); 
    }
    return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    }

  function updateIsoTime(timeInHHMM, fullIsoTime) {
    // Updates the time portion of an ISO date string with the given HH:MM time.
    const [hours, minutes] = timeInHHMM.split(':');
    const seconds = "00";
    const isoDate = new Date(fullIsoTime);

    isoDate.setHours(hours);
    isoDate.setMinutes(minutes);
    isoDate.setSeconds(seconds);

    return isoDate.toISOString();
  }

  function openForm(timestamp  = null) {
    // Opens the form for creating or editing a timestamp.
    if (timestamp && timestamp.id) {
        // Editing existing timestamp
        console.log("reading timestamp")
        isEditing.value = true;
        entryId.value = timestamp.id;
        IsoInTime.value = timestamp.inTime;
        IsoOutTime.value = timestamp.inTime;
        inTime.value = timestamp.inTime ? formatTime(timestamp.inTime): null;
        outTime.value = timestamp.outTime ? formatTime(timestamp.outTime): null;
        description.value = timestamp.description;
        reportingType.value = timestamp.reporting_type; 
    } else {
        // Creating new timestamp
        isEditing.value = false;
        const day = timestamp.getDate(); 
        const month = timestamp.getMonth(); 
        const year = timestamp.getFullYear();
        console.log(day, month, year);
        IsoInTime.value = new Date(year, month, day,1,1,1);
        IsoOutTime.value = new Date(year, month, day,1,1,1);
        reportingType.value = 'work';

        resetForm();
    }
    showForm.value = true;
  }
  
  function resetForm() {
    // Resets the form fields and validation.
    inTime.value = null;
    outTime.value = null;
    description.value = null;
    if (form.value) {
      form.value.resetValidation();
    }
  }
  
  const submitForm = async () => {
    // Submits the form to create or update a timestamp.
    try {
        console.log('Submitting:', {
            entryId: entryId.value,
            inTime: inTime.value,
            outTime: outTime.value,
            description: description.value,
            isoin: IsoInTime.value,
            isoout: IsoOutTime.value,
            reporting_type: reportingType.value,
        });
        
        const method = isEditing.value ? 'put' : 'post';
        const url = isEditing.value
        ? `${endpoints.timestamps.edit}/${entryId.value}` 
        : endpoints.timestamps.create;

        const response = await api({
        method,
        url,
        headers: {
            'Content-Type': 'application/json',
        },
        data: {
            punch_in_timestamp: reportingType.value === 'work' ? updateIsoTime(inTime.value, IsoInTime.value) : updateIsoTime('00:00', IsoInTime.value), 
            punch_out_timestamp: reportingType.value === 'work' ? updateIsoTime(outTime.value, IsoOutTime.value) : updateIsoTime('00:00', IsoOutTime.value), 
            detail: description.value,
            punch_type: 1,
            reporting_type: reportingType.value,
             
            ...( isEditing.value ? {} : {
                user_email: props.selectedUser, 
                }),
            }
        });
  
        if (isEditing.value) {
            console.log('Timestamp updated successfully');
            emit('timestampUpdated'); 
        } else {
            console.log('Timestamp created successfully');
            emit('timestampCreated'); 
        }
        showForm.value = false; 
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };
  
  function validateEndTime(endTime) {
    // Validates that the end time is later than the start time.
    if (!endTime || !inTime.value) return true; 

    const [endHours, endMinutes] = endTime.split(':').map(Number);
    const [startHours, startMinutes] = inTime.value.split(':').map(Number);

    if (endHours > startHours || (endHours === startHours && endMinutes >= startMinutes)) {
      return true;
    } else {
      return 'End time must be later than Start Time';
    }
  }

  defineExpose({ openForm });
</script>


<template>
  <VDialog v-model="showForm" persistent max-width="600px">
    <VCard>
      <VCardTitle>
        <span class="headline">{{ isEditing ? 'Edit Timestamp' : 'Add New Timestamp' }}</span>
      </VCardTitle>
      <VCardText>
        <VForm ref="form" @submit.prevent="submitForm">
          <VCol cols="12">
            <VSelect
              v-model="reportingType"
              :items="reportingTypeOptions"
              label="Reporting Type"
              :rules="[requiredRule]"
            />
          </VCol>
          <VRow>
            <VCol v-if="reportingType === 'work'" cols="12">
              <VTextField
                v-model="inTime"
                label="Start Time"
                type="time"
                :rules="[requiredRule]"
              />
            </VCol>
            <VCol v-if="reportingType === 'work'" cols="12">
              <VTextField
                v-model="outTime"
                label="End Time"
                type="time"
                :rules="[requiredRule, validateEndTime]"
              />
            </VCol>
            <VCol cols="12"> 
              <VTextField 
                v-model="description" 
                label="Description" 
                placeholder="Add a description" 
              />
            </VCol>
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
              <VBtn type="submit" :disabled="!isFormValid && reportingType === 'work'">
                {{ isEditing ? 'Update' : 'Submit' }}
              </VBtn>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>
  </VDialog>
</template>