<template>
  <div class="relative min-h-screen flex flex-col items-center justify-center">
    <video autoplay muted loop id="myVideo" class="absolute top-0 left-0 w-full h-full object-cover">
      <source src="@/assets/SignUpVideo.mp4" type="video/mp4">
      Your browser does not support HTML5 video.
    </video>
    <div class="absolute top-0 left-0 w-full h-full bg-black opacity-50"></div>
    <div class="w-full max-w-md px-6 py-8 mb-4 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
      <h2 class="text-3xl font-extrabold text-center text-gray-900">Sign Up</h2>
      <p class="mt-2 text-sm text-center text-gray-600">
        Welcome to our Social Media App! Sign up to get started.
      </p>
      <p class="mt-4 text-center">
        Already have an account?
        <RouterLink :to="{'name':'signin'}" class="text-blue-600 underline">Click here to login!</RouterLink>
      </p>
      <form class="mt-8 space-y-6" @submit.prevent="submitForm">
        <div>
          <div class="mb-4">
            <label for="name" class="sr-only">Username</label>
            <input id="name" type="text" v-model="form.username" required class="block w-full px-3 py-2 mb-3 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" placeholder="Your social media username">
          </div>
          <div class="mb-4">
            <label for="displayName" class="sr-only">Display Name</label>
            <input id="displayName" type="text" v-model="form.displayName" required class="block w-full px-3 py-2 mb-3 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" placeholder="Display Name">
          </div>
          <div class="mb-4">
            <label for="github" class="sr-only">GitHub URL</label>
            <input id="github" type="url" v-model="form.github" class="block w-full px-3 py-2 mb-3 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" placeholder="GitHub URL">
          </div>
          <div class="mb-4">
            <label for="password" class="sr-only">Password</label>
            <input id="password" type="password" v-model="form.password" required class="block w-full px-3 py-2 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" placeholder="Your password">
          </div>
          <div class="mb-4">
            <label for="repeat-password" class="sr-only">Repeat Password</label>
            <input id="repeat-password" type="password" v-model="form.repeatPassword" required class="block w-full px-3 py-2 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" placeholder="Repeat your password">
          </div>
          <div class="mb-4">
            <label for="profilePicture" class="sr-only">Profile Picture</label>
            <input id="profilePicture" type="file" @change="onFileChange" class="block w-full px-3 py-2 mb-3 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" placeholder="Upload Profile Picture">
          </div>
          <button type="submit" class="flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Sign Up</button>
        </div>
      </form>
      <div v-if="errors.length" class="mt-4">
        <ul class="list-disc">
          <li v-for="error in errors" :key="error" class="text-red-500">{{ error }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});
// console.log('url signup :', process.env.VUE_APP_API_URL);
export default {
  data() {
    return {
      form: {
        username: '',
        displayName: '',
        password: '',
        repeatPassword: '',
        github: '',
        profilePicture: null,
      },
      errors: [],
    };
  },
  methods: {
    onFileChange(event) {
      this.form.profilePicture = event.target.files[0];
    },
    submitForm() {
  this.errors = [];
  if (!this.form.username) {
    this.errors.push("Username required.");
  }
  if (!this.form.displayName) {
    this.errors.push("Display Name required.");
  }
  if (!this.form.password) {
    this.errors.push("Password required.");
  }
  if (!this.form.repeatPassword) {
    this.errors.push("Repeat Password required.");
  }
  

  if (this.errors.length === 0) {
    const formData = new FormData();
    formData.append('username', this.form.username);
    formData.append('displayName', this.form.displayName);
    formData.append('password', this.form.password);
    formData.append('password2', this.form.repeatPassword); 
    formData.append('github', this.form.github);
    if (this.form.profilePicture) {
      formData.append('profilePictureImage', this.form.profilePicture); 
    }

    apiClient.post('/signup/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
      .then(response => {
        if (response.status === 201) {
          alert("Sign up successful!");
          this.$router.push({ name: 'signin' });
        } else {
          alert("Sign up failed! Please try again.");
        }
      })
      
      .catch(error => {
      // Check if the error response object exists
      if (error.response && error.response.data) {
        // If there are specific error messages from the backend, add them to the errors array
        if (error.response.data) {
          for (const key in error.response.data) {
            if (error.response.data.hasOwnProperty(key)) {
              this.errors.push(`${key}: ${error.response.data[key]}`);
            }
          }
        } else {
          this.errors.push("An unknown error occurred.");
        }
      } else {
        // If there is no response, it means the request never left or there was no response
        this.errors.push("Server error: Could not connect to the server.");
      }
    }
      
  );
  }
},

  },
};
</script>

<style scoped>
#myVideo {
  position: fixed;
  right: 0;
  bottom: 0;
  min-width: 100%;
  min-height: 100%;
  z-index: 0;
}

.content {
  z-index: 10;
}
</style>