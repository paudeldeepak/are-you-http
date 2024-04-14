<template>
	<head>
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
		<link rel="stylesheet"
			href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css">
	</head>
	<DefaultLayout>
		<div class="create-post-container">
			<form @submit.prevent="submitPost">

				<!-- ContentType Field -->
				<div class="form-group">
					<label for="postContentType">Content Type</label>
					<select id="postContentType" v-model="post.contentType" required>
						<option value="text/plain">Plain Text</option>
						<option value="text/markdown">Markdown</option>
						<option value="image/png;base64">PNG Image</option>
						<option value="image/jpeg;base64">JPEG Image</option>
					</select>
				</div>

				<!-- Title Field -->
				<div class="form-group">
					<label for="postTitle">Title</label>
					<input type="text" id="postTitle" v-model="post.title" required />
				</div>

				<!-- Content Field -->
				<div v-if="!isImageContentType" class="form-group">
					<div class="content-label-and-preview-button">
						<label for="postContent" class="content-label">Content</label>
						<button type="button" class="markdown-preview-button" @click="togglePreview"
							:disabled="!post.content.trim()" v-if="post.contentType === 'text/markdown'">
							{{ showPreview ? 'Hide Preview' : 'Show Preview' }}
						</button>
					</div>
					<textarea id="postContent" v-model="post.content" required></textarea>
				</div>

				<!-- Markdown Preview Title and Preview Pane -->
				<div v-if="showPreview && post.contentType === 'text/markdown'" class="markdown-preview">
					<div class="markdown-body" v-html="renderMarkdown(post.content)"></div>
				</div>

				<!-- Description Field -->
				<div v-if="!isImageContentType" class="form-group">
					<label for="postDescription">Description</label>
					<textarea id="postDescription" v-model="post.description"></textarea>
				</div>

				<!-- Image Upload Information, Shown Only when image is uploaded and then displays image name-->
				<div v-if="isImageContentType && post.image">
					<p>Uploaded Image: {{ getImageName }}</p>
					<!-- Image Preview -->
					<img v-if="post.content" :src="post.content" alt="Image preview"
						style="max-width: 100%; max-height: 300px;" />
				</div>
				<!-- Image Upload Field, Shown Only if ContentType is an Image Type -->
				<div class="form-group" v-if="isImageContentType">
					<input type="file" id="imageUpload" @change="handleImageUpload" :accept="acceptedFileTypes" />
					<label for="imageUpload">Click to upload image</label>
				</div>

				<!-- Visibility Field -->
				<div class="form-group">
					<label for="postVisibility">Visibility</label>
					<select id="postVisibility" v-model="post.visibility" required>
						<option value="PUBLIC">Public</option>
						<option value="FRIENDS">Friends</option>
						<option value="UNLISTED">Unlisted</option>
					</select>
				</div>

				<!-- Submission Button -->
				<button type="submit">Post</button>
			</form>
		</div>
	</DefaultLayout>
</template>

<script>
import axios from "axios";
import DefaultLayout from "@/components/DefaultLayout.vue";
import { marked } from 'marked';
import DOMPurify from 'dompurify';

export default {
	components: {
		DefaultLayout,
	},
	data() {
		return {
			HOST_URL: import.meta.env.VITE_API_URL,
			post: {
				title: "",
				content: "", // This will also hold the Base64 image data for image posts
				description: "",
				contentType: "text/plain",
				visibility: "PUBLIC",
				image: null, // Holds the image file for reference, not used directly in submission 
			},
			
			showPreview: false // Flag to show/hide the markdown preview
		};
		
	},
	
	
	computed: {
		isImageContentType() {
			return this.post.contentType === "image/png;base64" || this.post.contentType === "image/jpeg;base64";
		},
		acceptedFileTypes() {
			if (this.post.contentType === "image/png;base64") {
				return ".png";
			} else if (this.post.contentType === "image/jpeg;base64") {
				return ".jpeg, .jpg";
			}
			return ""; // Default case, though this shouldn't happen as the input is hidden for non-image content types
		},
		getImageName() {
			if (this.post.image && this.post.image.name) {
				return this.post.image.name;
			}
			return 'No image selected';
		},
	},

	methods: {
		handleImageUpload(event) {
			const file = event.target.files[0];
			if (file && (file.type === "image/png" || file.type === "image/jpeg")) {
				this.post.image = file;
				const reader = new FileReader();
				reader.onload = (e) => {
					this.post.content = e.target.result;
					this.post.contentType = file.type + ";base64";
				};
				reader.readAsDataURL(file);
			}
		},
		renderMarkdown(content) {
			const rawMarkup = marked(content);
			return DOMPurify.sanitize(rawMarkup);
		},
		togglePreview() {
			if (this.post.content.trim()) {
				this.showPreview = !this.showPreview;
			}
		},
	
		submitPost() {
			const userId = localStorage.getItem("userId");
			const authToken = localStorage.getItem("userToken");

			const formData = new FormData();
			formData.append("title", this.post.title);
			formData.append("content", this.post.content); // Base64 image data is directly included here for image posts
			formData.append("description", this.post.description);
			formData.append("contentType", this.post.contentType);
			formData.append("visibility", this.post.visibility);

			axios
				.post(`${this.HOST_URL}/authors/${userId}/posts/`, formData, {
					headers: {
						Authorization: `Token ${authToken}`,
					},
				})
				.then((response) => {
					alert("Post successfully created!");
					// Redirect to the user's profile page
					this.$router.push(`/profile/${userId}`);
				})
				.catch((error) => {
					console.error("There was an error submitting the post:", error);
					// Handle error
				});
		},
	},
};


</script>

<style scoped>
.create-post-container {
	background-color: #fff;
	border: 1px solid #ccc;
	border-radius: 10px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	padding: 20px;
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

.content-group {
	display: flex;
	flex-direction: column;
}

.content-with-preview {
	display: flex;
	align-items: center;
	gap: 10px;
}

.content-with-preview textarea {
	flex-grow: 1;
}

.markdown-preview {
	border: 1px solid #ccc;
	margin-top: 20px;
	margin-bottom: 20px;
	padding: 10px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

button {
	background-color: #70d19c;
	color: white;
	border: none;
	padding: 10px 15px;
	border-radius: 6px;
	cursor: pointer;
	font-size: 16px;
	font-weight: bold;
	text-transform: uppercase;
}

button:hover {
	background-color: #088848;
}

.markdown-preview-button {
	background-color: #70d19c;
	/* A different color for the Markdown preview button */
	color: white;
	border: none;
	padding: 8px 16px;
	border-radius: 4px;
	cursor: pointer;
	transition: background-color 0.3s ease;
}

.markdown-preview-button:hover {
	background-color: #088848;
	/* A slightly darker color on hover */
}

.content-label-and-preview-button {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 5px;
}

.content-label {
	margin-bottom: 0;
	/* Remove the margin if not needed */
}

.markdown-preview-button:disabled {
	background-color: #ccc;
	color: #666;
	cursor: not-allowed;
}
</style>