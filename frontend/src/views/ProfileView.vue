<template>

	<head>
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
		<link
			rel="stylesheet"
			href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css"
		/>
	</head>
	<DefaultLayout>
		<div class="profile-header">
			<div class="profile-picture-wrapper">
				<img :src="fullPictureUrl" alt="Profile Picture" class="profile-picture" />
			</div>
			<div class="profile-info">
				<a v-if="profile.github" :href="profile.github" target="_blank" class="github-link"
					rel="noopener noreferrer">
					GitHub: <i class="fab fa-github"></i>
				</a>
				<p class="profile-username">Username: {{ profile.username }}</p>
				<h1 class="profile-name">Name: {{ profile.displayName }}</h1>
				<div v-if="isAuthor">
				<button @click="navigateToEditProfile()" class="edit-profile-btn">Edit Profile</button>
				</div>
			</div>
		</div>
		<div class="posts-container">
			<h2 class="recent-posts-title">Recent Posts</h2>
			<div class="post" v-for="post in userPosts" :key="post.id">
				<div class="post-header">
					<img :src="fullPictureUrl" alt="Profile Picture" class="post-profile-picture" />
					<div class="post-info">
						<p class="post-username">{{ profile.username }}</p>
						<p class="post-timestamp">{{ formatDate(post.published) }}</p>
					</div>
					<div v-if="isAuthor">
						<router-link :to="`/authors/${profile.id}/posts/${getPostId(post.id)}/edit`"
							class="edit-post-button">
							<i class="fa fa-edit"></i> Edit Post
						</router-link>
					</div>
					<div v-if="isAuthor">
						<button @click="deletePost(post.id)" class="delete-post-button">
							<i class="fas fa-trash-alt"></i> Delete
						</button>
					</div>
					<div v-if="isAuthor">
						<button @click="sharePost(this.getPostId(post.id),post.author.uid)" class="share-post-button">
							<i class="fa-solid fa-share"></i> Share
						</button>
					</div>
				</div>
				<div class="post-content">
					<h3 class="post-title">{{ post.title }}</h3>
					<div v-if="isImageContentType(post.contentType)">
						<img :src="post.content" alt="Post Image" class="post-image" />
					</div>
					<div
						v-else-if="post.contentType === 'text/markdown'"
						class="markdown-body"
						v-html="renderMarkdown(post.content)"
					></div>
					<p v-else>{{ post.content }}</p>
				</div>
			</div>
		</div>
	</DefaultLayout>
</template>


<script>
import axios from "axios";
import { RouterLink } from "vue-router";
import DefaultLayout from "@/components/DefaultLayout.vue";
import { marked } from "marked";
import DOMPurify from "dompurify";

export default {
	components: {
		DefaultLayout,
		RouterLink,
	},
	data() {
		// console.log('Environment PROFILE:', process.env.NODE_ENV);
		// console.log("API URL PROFILE:", process.env.VUE_APP_API_URL);
  		
		return {
			
			HOST_URL: import.meta.env.VITE_API_URL,
			

        	userPosts: [],
			userPosts: [],
			profile: {
				picture: "",
				displayName: "",
				username: "",
				github: "",
				id: "",
			},
			githubActivities: [],
			defaultImage: "https://via.placeholder.com/150",
		};
	},
	computed: {
		fullPictureUrl() {
			return this.profile.picture || this.defaultImage;
		},
		isAuthor() {
			const loggedInUserId = localStorage.getItem('userId');
			// console.log('loggedInUserId:', loggedInUserId);
			
			return loggedInUserId === this.profile.id.toString();
		},
		githubUsername() {
			if (this.profile.github) {
				const parts = this.profile.github.split("/");
				return parts[parts.length - 1];
			}
			return "";
		},
	},
	async created() {
		await this.fetchUserProfile();
		await this.fetchGithubActivities();
		await this.fetchUserPosts();
	},
	methods: {
		isImageContentType(contentType) {
			return contentType === "image/png;base64" || contentType === "image/jpeg;base64";
		},
		getActivityType(type) {
			return type.replace("Event", "");
		},
		formatDate(dateString) {
			const options = {
				year: "numeric",
				month: "long",
				day: "numeric",
				hour: "numeric",
				minute: "numeric",
				second: "numeric",
				timeZoneName: "short",
			};
			return new Date(dateString).toLocaleString(undefined, options);
		},
		navigateToEditProfile() {
			// print('navigateToEditProfile_profile_id:', this.profile.id)
			if (this.profile.id) {
				this.$router.push({ name: "edit-profile", params: { authorId: this.profile.id } });
			} else {
				console.error("No author ID found.");
			}
		},
		async fetchUserPosts() {
			// console.log('HOST_URL in fetch user posts:', this.HOST_URL);

			const authorId = this.$route.params.authorId;
			const authToken = localStorage.getItem("userToken");
			if (!authorId || !authToken) {
				console.error("Author ID or Auth Token not found.");
				return;
			}
			try {
				const response = await axios.get(`${this.HOST_URL}/authors/${authorId}/posts/`, {
					headers: {
						"Authorization": `Token ${authToken}`,
					},
				});
				this.userPosts = response.data;
			} catch (error) {
				console.error("Error fetching user posts:", error);
			}
		},
		async fetchUserProfile() {
			const authorId = this.$route.params.authorId;
			// print('authorId in fetch user profile:', authorId)
			if (!authorId) {
				console.error("No author ID found.");
				return;
			}
			// print('this is before the try catch block in fetch user profile:')
			try {
				const authToken = localStorage.getItem('userToken');
				// print('authToken:', authToken)
				
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				// console.log('HOST_URL in fetch user profile:', this.HOST_URL);
				const response = await axios.get(`${this.HOST_URL}/authors/${authorId}/`,
				 {
					headers: {
						'Authorization': `Token ${authToken}`,
						
					},
				});
				this.profile = {
					node: response.data.node,
					picture: response.data.profileImage,
					displayName: response.data.displayName,
					username: response.data.username,
					github: response.data.github,
					id: authorId,
					
				};
				console.log('Fetched user profile:', this.profile);
			} catch (error) {
				// console.log('I AM IN FETCH USER PROFILE ERROR')
				console.error("Error fetching user profile:", error);
			}
		},
		async sharePost(postId, selectedAuthors) {
			// Construct the URL of the post
			const postUrl = `${window.location.origin}/posts/${selectedAuthors}/${postId}`;

			// Check if the browser supports the Web Share API
			if (navigator.share) {
				// Use the Web Share API to share the post URL
				try {
					await navigator.share({
						title: "Share Post",
						text: "Check out this post!",
						url: postUrl,
					});
					console.log("Post shared successfully");
				} catch (error) {
					console.error("Error sharing post:", error);
				}
			} else {
				// Fallback for browsers that do not support the Web Share API
				// You can implement a custom sharing feature here
				console.log("Web Share API not supported");
				// Example: Copying the post URL to the clipboard
				try {
					await navigator.clipboard.writeText(postUrl);
					console.log("Post URL copied to clipboard");
					// You can show a notification to the user that the URL has been copied
				} catch (error) {
					console.error("Error copying post URL to clipboard:", error);
				}
			}
		},

		async fetchGithubActivities() {
			const username = this.githubUsername;
			if (username) {
				try {
					const response = await axios.get(`https://api.github.com/users/${username}/events`);
					const activities = response.data.slice(0, 10); // Fetch the latest 10 activities
					await Promise.all(activities.map(activity => {
						const uniqueIdentifier = `${activity.id}`;
						return this.processActivity(activity, uniqueIdentifier);
					}));
				} catch (error) {
					console.error("Error fetching GitHub activities:", error);
				}
			}
		},
		async processActivity(activity, uniqueIdentifier) {
			await this.fetchUserPosts();
			const isAlreadyPosted = this.userPosts.some(post => post.description && post.description.includes(uniqueIdentifier));
			if (!isAlreadyPosted) {
				await this.createPostFromActivity(activity, uniqueIdentifier);
			}
		},
		async createPostFromActivity(activity, uniqueIdentifier) {
			const postContent = this.renderActivity(activity);
			const newPost = {
				title: `Github: ${this.getActivityType(activity.type)} - ${new Date(activity.created_at).toLocaleDateString()}`,
				content: postContent,
				description: uniqueIdentifier, // Store the unique identifier in the description field
				contentType: 'text/markdown',
				visibility: 'PUBLIC',
				unlisted: false,
			};
			try {
				await axios.post(`${this.HOST_URL}/authors/${this.profile.id}/posts/`, newPost, {
					headers: { 'Authorization': `Token ${localStorage.getItem('userToken')}` },
				});
			} catch (error) {
				console.error("Error creating post from GitHub activity:", error);
			}
		},
		renderActivity(activity) {
			let content = `**Event**: ${activity.type}\n**Repository**: [${activity.repo.name}](https://github.com/${activity.repo.name})\n`;

			switch (activity.type) {
				case 'PushEvent':
					content += `**Commits**:\n`;
					activity.payload.commits.forEach(commit => {
						const commitUrl = `https://github.com/${activity.repo.name}/commit/${commit.sha}`;
						content += `- [${commit.sha.substring(0, 7)}](${commitUrl}) - ${commit.message}\n`;
					});
					break;
				case 'ForkEvent':
					content += `Forked to [${activity.payload.forkee.full_name}](https://github.com/${activity.payload.forkee.full_name})\n`;
					break;
				case 'PullRequestEvent':
					const pr = activity.payload.pull_request;
					content += `**Pull Request**: [#${pr.number} ${pr.title}](${pr.html_url})\n**Status**: ${pr.state}\n**Created At**: ${new Date(pr.created_at).toLocaleDateString()}\n`;
					break;
				case 'PublicEvent':
					content += `**Action**: Repository made public\n`;
					break;
				default:
					content += `This event type (${activity.type}) is not specifically formatted.`;
					break;
			}

			return content;
		},
		async deletePost(postUrl) {
			const postId = this.getPostId(postUrl);
			const authorId = this.$route.params.authorId;
			if (!postId) {
				console.error("Invalid post ID.");
				return;
			}
			if (!authorId) {
				console.error("Invalid author ID.");
				return;
			}
			const deleteUrl = `${this.HOST_URL}/authors/${authorId}/posts/${postId}`;
			const headers = {
				Authorization: `Token ${localStorage.getItem("userToken")}`,
			};
			try {
				const response = await axios.delete(deleteUrl, { headers });
				if (response.status === 204) {
					alert("Post deleted successfully.");
					await this.fetchUserPosts();
				} else {
					console.error("Failed to delete post. Unexpected status:", response.status);
				}
			} catch (error) {
				console.error("Error deleting post:", error);
			}
		},
		formatDate(value) {
			if (value) {
				return new Date(value).toLocaleString();
			}
			return "";
		},
		renderMarkdown(content) {
			return DOMPurify.sanitize(marked(content));
		},
		getPostId(postUrl) {
			return postUrl.substring(postUrl.lastIndexOf("/") + 1);
		},
	},
};
</script>


<style scoped>
/* Post Content Improvements */
.post-content {
	background-color: #fff;
	border: 1px solid #e1e4e8;
	border-radius: 6px;
	padding: 20px;
	margin-top: 10px;
}


.edit-post-button,
.delete-post-button {
	font-size: 0.8em;
	padding: 5px 10px;
}

.profile-header {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 20px;
	border-bottom: 2px solid #eee;
	background: #fff;
	border-radius: 10px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	margin-bottom: 20px;
}

.profile-picture-wrapper {
	width: 150px;
	height: 150px;
	border-radius: 50%;
	overflow: hidden;
	margin-bottom: 20px;
	background-color: #f0f0f0;
	display: flex;
	justify-content: center;
	align-items: center;
}

.profile-picture {
	width: 100%;
	height: 100%;
	border-radius: 50%;
	object-fit: fill;
}

.profile-info {
	text-align: center;
	margin-bottom: 20px;
}

.profile-username {
	margin: 0;
	font-size: 0.875rem;
	color: #333;
	margin-bottom: 0.5rem;
	font-weight: 600;
}

.profile-name {
	margin: 0;
	font-size: 0.875rem;
	color: #333;
	margin-bottom: 0.5rem;
	font-weight: 600;
}

.edit-profile-btn {
	background-color: #4CAF50;
	color: white;
	padding: 10px 20px;
	border: none;
	border-radius: 4px;
	cursor: pointer;
	transition: background-color 0.3s ease;
	font-size: 0.875rem;
}

.edit-profile-btn:hover {
	background-color: #45a049;
}

.github-link {
	display: inline-block;
	margin-top: 10px;
	color: #333;
	text-decoration: none;
	font-size: 0.875rem;
	font-weight: bold;
}

.fab.fa-github {
	font-size: 1.5rem;
	margin-left: 5px;
	vertical-align: middle;
}

.posts-container {
	margin: auto;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	padding: 20px;
	border: 1px solid #ccc;
	border-radius: 10px;
}

.post {
	background-color: #fff;
	border: 1px solid #ccc;
	border-radius: 10px;
	margin-bottom: 20px;
	padding: 15px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.post-image {
	max-width: 100%;
	height: auto;
	margin-top: 10px;
}

.post-header {
	display: flex;
	align-items: center;
	margin-bottom: 15px;
}

.post-profile-picture {
	border-radius: 50%;
	width: 40px;
	height: 40px;
	object-fit: cover;
	border: 2px solid #ddd;
	margin-right: 10px;
}

.post-info {
	flex-grow: 1;
}

.post-username {
	margin: 0;
	font-weight: bold;
}

.post-timestamp {
	margin: 0;
	font-size: 0.85em;
	color: #606770;
}

.post-content h3 {
	margin-top: 0;
}

.post-content p {
	white-space: pre-wrap;
}

.recent-posts-title {
	font-size: 23px;
	margin-left: 3px;
	margin-bottom: 10px;
	font-weight: bold;
}

.post-title {
	font-weight: bold;
}

.edit-post-button {
	display: inline-block;
	margin: 5px;
	background-color: #4caf50;
	color: white;
	padding: 5px 10px;
	border-radius: 4px;
	text-decoration: none;
	border-radius: 10px;
}

.edit-post-button:hover {
	background-color: #45a049;
}

.delete-post-button {
	display: inline-block;
	margin: 5px;
	background-color: #aa4a44;
	color: white;
	padding: 5px 10px;
	border-radius: 4px;
	text-decoration: none;
	border-radius: 10px;
}

.delete-post-button:hover {
	background-color: #7a0707;
}

.share-post-button {
	font-size: 0.8em;
	color: #ffffff;
	margin-right: 7px;
	border-radius: 9px;
	padding: 4px 6px;
	background-color: #3492c5;
}

.share-post-button:hover {
	background-color: #3087b5;
}
</style>
