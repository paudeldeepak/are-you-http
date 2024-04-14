<template>

	<head>
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
		<link rel="stylesheet"
			href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css">
	</head>
	<DefaultLayout>
		<div class="edit-profile-container">
			<h1>Edit Profile</h1>
			<form @submit.prevent="updateProfile">
				<div class="form-group">
					<label for="displayName">Name:</label>
					<input type="text" id="displayName" v-model="profile.displayName" required>
				</div>
				<div class="form-group">
					<label for="username">Username:</label>
					<input type="text" id="username" v-model="profile.username" required>
				</div>
				<div class="form-group" v-if="imagePreview">
					<img :src="imagePreview" class="image-preview" alt="Profile preview" />
				</div>
				<div class="form-group">
					<input type="file" id="imageUpload" @change="onFileChange" />
					<label for="imageUpload">Update Profile Image</label>
				</div>
				<div class="actions">
					<button type="submit" class="save-btn">Save Changes</button>
				</div>
			</form>
		</div>
	</DefaultLayout>
</template>

<script>
import DefaultLayout from "@/components/DefaultLayout.vue";
import axios from "axios";

export default {
	components: {
		DefaultLayout
	},
	data() {
		return {
			HOST_URL:import.meta.env.VITE_API_URL,
			profile: {
				displayName: "",
				username: "",
				picture: null,
			},
			imagePreview: null,
		};
	},
	methods: {
		onFileChange(e) {
			const file = e.target.files[0];
			this.profile.picture = file;
			if (file) {
				this.imagePreview = URL.createObjectURL(file);
			}
		},

		async updateProfile() {
			const authorId = this.$route.params.authorId;
			const formData = new FormData();
			formData.append('displayName', this.profile.displayName);
			formData.append('username', this.profile.username);
			if (this.profile.picture) {
				formData.append('profilePictureImage', this.profile.picture);
			}

			const authToken = localStorage.getItem('userToken');

			try {
				await axios.put(`${this.HOST_URL}/authors/${authorId}/`, formData, {
					headers: {
						'Authorization': `Token ${authToken}`,
						'Content-Type': 'multipart/form-data'
					}
				});
				alert("Profile updated successfully!");
				this.$router.push(`/profile/${authorId}`);
			} catch (error) {
				console.error("Error updating profile:", error);
				alert("Failed to update profile.");
			}
		},

		async fetchUserProfile() {
			const authorId = this.$route.params.authorId;
			const authToken = localStorage.getItem('userToken');

			try {
				const response = await axios.get(`${this.HOST_URL}/authors/${authorId}/`, {
					headers: {
						'Authorization': `Token ${authToken}`,
					}
				});
				this.profile.displayName = response.data.displayName;
				this.profile.username = response.data.username;
				// Handle the profile picture URL
			} catch (error) {
				console.error("Error fetching user profile:", error);
			}
		}
	},
	created() {
		this.fetchUserProfile();
	}
};
</script>


<style scoped>
.edit-profile-container {
	max-width: 600px;
	margin: 2rem auto;
	padding: 2rem;
	background-color: #fff;
	border-radius: 8px;
	box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
	margin-bottom: 15px;
}

.form-group label {
	display: block;
	font-weight: bold;
	margin-bottom: 5px;
}

.form-group input[type="text"],
.form-group textarea,
.form-group select {
	width: 100%;
	padding: 8px;
	border: 1px solid #ddd;
	border-radius: 6px;
	margin-bottom: 10px;
}

.form-group input[type="file"] {
	display: none;
}

.form-group label[for="imageUpload"] {
	background-color: #f0f2f5;
	border: 1px dashed #ccd0d5;
	padding: 10px;
	border-radius: 6px;
	cursor: pointer;
	text-align: center;
}

.form-group label[for="imageUpload"]:hover {
	background-color: #e4e6e9;
}

.actions {
	margin-top: 1rem;
	display: flex;
	justify-content: center;
}

.save-btn {
	background-color: #70d19c;
	color: #fff;
	padding: 0.5rem 1rem;
	border-radius: 4px;
	cursor: pointer;
	font-size: 1rem;
	border: none;
	transition: background-color 0.3s;
}

.save-btn:hover {
	background-color: #45a049;
}

.image-preview {
	width: 100%;
	max-width: 200px;
	height: auto;
	margin-top: 15px;
	border-radius: 8px;
	border: 1px solid #ddd;
}

h1 {
	text-align: center;
	color: #333;
	font-size: 1.5rem;
	margin-bottom: 1.5rem;
}
</style>