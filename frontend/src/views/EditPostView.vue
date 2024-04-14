<template>
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
        <link rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css">
    </head>
    <DefaultLayout>
        <div class="create-post-container">
            <form @submit.prevent="submitUpdatedPost">

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

                <!-- Image Previw-->
                <div v-if="isImageContentType">
                    <p>Uploaded Image:</p>
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
                <button type="submit">Update Post</button>
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
                content: "",
                description: "",
                contentType: "text/plain",
                visibility: "PUBLIC",
            },
            postId: this.$route.params.postId,
            showPreview: false,
        };
    },
    computed: {
        isImageContentType() {
            return this.post.contentType.includes("image/");
        },
        acceptedFileTypes() {
            if (this.post.contentType.includes("image/png")) {
                return ".png";
            } else if (this.post.contentType.includes("image/jpeg")) {
                return ".jpeg, .jpg";
            }
            return "";
        },
    },
    async created() {
        await this.fetchPostDetails();
    },
    methods: {
        async fetchPostDetails() {
            try {
                const response = await axios.get(`${this.HOST_URL}/authors/${this.$route.params.authorId}/posts/${this.postId}`, {
                    headers: {
                        'Authorization': `Token ${localStorage.getItem("userToken")}`,
                    },
                });
                this.post = { ...response.data };
            } catch (error) {
                console.error("Error fetching post details:", error);
            }
        },
        handleImageUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.post.content = e.target.result;
                    this.post.contentType = `image/${file.type.split("/")[1]};base64`;
                };
                reader.readAsDataURL(file);
            }
        },
        renderMarkdown(content) {
            return DOMPurify.sanitize(marked(content));
        },
        togglePreview() {
            if (this.post.content.trim()) {
                this.showPreview = !this.showPreview;
            }
        },
        async submitUpdatedPost() {
            try {
                await axios.put(`${this.HOST_URL}/authors/${this.$route.params.authorId}/posts/${this.postId}`, this.post, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Token ${localStorage.getItem("userToken")}`,
                    },
                });
                alert("Post updated successfully.");
                this.$router.push(`/profile/${this.$route.params.authorId}`);
            } catch (error) {
                console.error("There was an error updating the post:", error);
            }
        },
    }
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