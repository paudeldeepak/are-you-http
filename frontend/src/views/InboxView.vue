<template>

	<head>
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
		<link rel="stylesheet"
			href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css" />
	</head>
	<DefaultLayout>
		<div class="inbox-container">
			<section class="follow-requests">
				<div class="section-header">
					<h2 class="section-title">Follow Requests</h2>
					<button @click="deleteAllInboxItems" class="delete-inbox-btn">Clear Inbox</button>
				</div>
				<div class="request-box">
					<ul class="request-list">
						<li v-for="request in followRequests" :key="request.id" class="request-item">
							<!-- Display profile photo -->
							<img :src="request.profilePhoto ? request.profilePhoto : defaultProfilePhoto"
								alt="Profile Photo" class="profile-photo" />
							<div class="profile-info">
								<h3>{{ request.displayName }}</h3>
								<p class="username">@{{ request.username }}</p>
							</div>
							<div>
								<button @click="acceptRequest(request.requestId)" class="button accept">Allow</button>
								<span class="button-space"></span>
								<button @click="denyRequest(request.requestId)" class="button deny">Deny</button>
							</div>
						</li>
					</ul>
				</div>
			</section>
			<section class="posts-section">
				<h2 class="section-title">Posts Notifications</h2>
				<div class="posts-list">
					<div v-if="sharedPosts.length === 0">
						No post notifications available.
					</div>
					<div v-for="post in sharedPosts" :key="post.id" class="post-item">
						<p>{{ post.senderUsername }} sent you a post!</p>
						<p class="post-timestamp">{{ formatDate(post.published) }}</p>
						<a :href="formatSharePostUrl(post.id)" target="_blank" class="view-post-link">View Post</a>
					</div>
				</div>
			</section>
			<section class="likes-section">
				<h2 class="section-title">Likes Notifications</h2>
				<div class="likes-list">
					<div v-if="likes.length === 0">
						No like notifications available.
					</div>
					<div v-for="like in likes" :key="like.object" class="like-item">
						<p>{{ like.summary }}</p>
						<p class="post-timestamp">{{ formatDate(like.published) }}</p>
						<a v-if="!like.summary.includes('comment')" :href="formatLikeURL(like.object)" target="_blank"
							class="view-like-link">View Post
						</a>
						<a v-else :href="formatCommentUrl(like.object, $route.params.authorId)" target="_blank"
							class="view-comment-link">View Post</a>
					</div>
				</div>
			</section>
			<section class="comments-section">
				<h2 class="section-title">Comments Notifications</h2>
				<div class="comments-list">
					<div v-if="comments.length === 0">
						No comment notifications available.
					</div>
					<div v-for="comment in comments" :key="comment.id" class="comment-item">
						<p>{{ comment.senderUsername }} commented on a post:</p>
						<p class="post-timestamp">{{ formatDate(comment.published) }}</p>
						<div v-html="renderMarkdown(comment.content)"></div>
						<a :href="formatCommentUrl(comment.id, $route.params.authorId)" target="_blank"
							class="view-comment-link">View Post</a>
					</div>
				</div>
			</section>
		</div>
	</DefaultLayout>
</template>

<script>
import DefaultLayout from "@/components/DefaultLayout.vue";
import axios from "axios";
import { marked } from "marked";
import DOMPurify from "dompurify";

export default {
	components: {
		DefaultLayout,
	},
	data() {
		return {
			HOST_URL: import.meta.env.VITE_API_URL,
			//defaultProfilePhoto: require('@/assets/default-profile-photo.jpg'),
			followRequests: [],

			sharedPosts: [],

			likes: [],
			comments: [],
		};
	},
	computed: {
		currentUser() {
			return localStorage.getItem("userId");
		},
	},
	created() {
		this.fetchFollowRequests();
		this.fetchSharedPosts();
		this.fetchComments();
		this.pollInboxUpdates();
	},
	methods: {

		pollInboxUpdates() {
			setInterval(async () => {
				await this.fetchFollowRequests();
				await this.fetchSharedPosts();
				await this.fetchComments();
			}, 5000); // Poll every 5 seconds
		},
		formatDate(value) {
			return value ? new Date(value).toLocaleString() : '';
		},
		renderMarkdown(content) {
			return DOMPurify.sanitize(marked.parse(content));
		},

		async acceptRequest(requestId) {
			try {
				const authorId = this.$route.params.authorId;
				const authToken = localStorage.getItem('userToken');

				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const index = this.followRequests.findIndex(req => req.id === requestId);

				if (index === -1) {
					console.error("Request not found.");
					return;
				}
				const request = this.followRequests[index];
				const foreignAuthorId = request.uid;
				console.log("Request object:", request);

				// Send a PUT request to accept the local follow request
				console.log("This is the first PUT request from this host and local author")
				const response = await axios.put(`${this.HOST_URL}/authors/${authorId}/followers/${foreignAuthorId}`, {}, {
					headers: {
						'Authorization': `Token ${authToken}`
					}
				});

				// console.log('Local follow request accepted:', response.data);

				// Remove the request from the list of follow requests
				this.followRequests.splice(index, 1);

				// console.log("before updateRemoteFriendshipStatus")
				// If the request is from a remote user, update the remote friendship status
				// if (request.is_remote) {
				// 	await this.updateRemoteFriendshipStatus(request.host, foreignAuthorId, authorId, request.token);
				// }
				// console.log("after updateRemoteFriendshipStatus")
			} catch (error) {
				console.error('Error accepting follow request:', error);
			}

		},
		formatCommentUrl(originalURL, authorId) {
			// Assuming originalURL format is like the example provided:
			// https://are-you-http-8-fc6ffef42d04.herokuapp.com/authors/ff9238c0-b5b8-489b-af10-44adbe030188/posts/e84923f4-e5a6-4a93-8c0f-7fbc66c7366d/comments/7592aec1-6516-49ec-982e-e9c844bc7e47
			// https://are-you-http-e20eaa26c5c5.herokuapp.com/authors/{authorId}/posts/{postId}/comments/{commentId}
			// Desired format is:
			// https://are-you-http-e20eaa26c5c5.herokuapp.com/posts/{authorId}/{postId}

			// Extract postId from the original URL
			const match = originalURL.match(/\/authors\/([^/]+)\/posts\/([^/]+)\/comments\/[^/]+$/);
			if (match && match.length === 3) {
				const [, , postId] = match;
				return `${this.HOST_URL}/posts/${authorId}/${postId}`;
			}

			return originalURL; // return the original URL if the pattern doesn't match
		},
		formatLikeURL(originalURL) {
			// Assuming originalURL format is:
			// https://are-you-http-d49f333cf532.herokuapp.com/authors/{authorId}/posts/{postId}
			// And desired format is:
			// https://are-you-http-e20eaa26c5c5.herokuapp.com/posts/{authorId}/{postId}

			// Extract the authorId and postId from the original URL
			const match = originalURL.match(/authors\/(.+?)\/posts\/(.+)$/);
			if (match && match.length >= 3) {
				let [_, authorId, postId] = match;
				// Check if the authorId is a UUID in compact format and format if necessary
				if (/^[0-9a-f]{32}$/i.test(authorId)) {
					authorId = authorId.replace(/^(.{8})(.{4})(.{4})(.{4})(.{12})$/, '$1-$2-$3-$4-$5');
				}
				// Check if the postId is a UUID in compact format and format if necessary
				if (/^[0-9a-f]{32}$/i.test(postId)) {
					postId = postId.replace(/^(.{8})(.{4})(.{4})(.{4})(.{12})$/, '$1-$2-$3-$4-$5');
				}
				return `${this.HOST_URL}/posts/${authorId}/${postId}`;
			}

			return originalURL; // Return the original URL if pattern doesn't match
		},
		formatSharePostUrl(originalURL) {
			// Assuming originalURL format is like the example provided:
			// https://are-you-http-e20eaa26c5c5.herokuapp.com/authors/{authorId}/posts/{postId}
			// Desired format is:
			// https://are-you-http-e20eaa26c5c5.herokuapp.com/posts/{authorId}/{postId}

			// Extract the authorId and postId from the original URL
			const match = originalURL.match(/\/authors\/([^/]+)\/posts\/([^/]+)$/);
			if (match && match.length === 3) {
				let [_, authorId, postId] = match;
				// Check if the authorId is a UUID in compact format and format if necessary
				if (/^[0-9a-f]{32}$/i.test(authorId)) {
					authorId = authorId.replace(/^(.{8})(.{4})(.{4})(.{4})(.{12})$/, '$1-$2-$3-$4-$5');
				}
				// Check if the postId is a UUID in compact format and format if necessary
				if (/^[0-9a-f]{32}$/i.test(postId)) {
					postId = postId.replace(/^(.{8})(.{4})(.{4})(.{4})(.{12})$/, '$1-$2-$3-$4-$5');
				}
				return `${this.HOST_URL}/posts/${authorId}/${postId}`;
			}

			// Return the original URL if the pattern doesn't match
			return originalURL;
		},
		async denyRequest(requestId) {
			// Implement the API call to deny the follow request

			try {
				const authorId = this.$route.params.authorId;
				const authToken = localStorage.getItem('userToken');

				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const index = this.followRequests.findIndex(req => req.id === requestId);

				if (index === -1) {
					console.error("Request not found.");
					return;
				}
				const request = this.followRequests[index];
				const foreignAuthorId = request.uid;


				// Send a delete request to delete the follow request
				const response = await axios.delete(`${this.HOST_URL}/authors/${authorId}/followers/${foreignAuthorId}`,
					{
						headers: {
							'Authorization': `Token ${authToken}`
						}
					}
				);

				// If the request is successful, you may want to update the UI or perform other actions
				console.log('Follow request denied:', response.data);
				this.followRequests.splice(index, 1);
			} catch (error) {
				console.error('Error denying follow request:', error);
			}
		},

		async fetchFollowRequests() {

			try {
				const authorId = this.$route.params.authorId;
				const authToken = localStorage.getItem('userToken');

				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				// console.log('=====token=====:', authToken);

				const response = await axios.get(`${this.HOST_URL}/authors/${authorId}/requests/`,

					{
						headers: { 'Authorization': `Token ${authToken}` },

					});
				//console.log('Author ID from InboxView:', authorId);
				console.log('Response from InboxView:', response.data);

				this.followRequests = response.data.map(item => ({
					uid: item.actor.uid,
					username: item.actor.username,
					displayName: item.actor.displayName,
					profilePhoto: item.actor.profileImage,
					is_remote: item.actor.is_remote,
					host: item.actor.host,
					token: item.actor.auth_token_key,

				}));
			} catch (error) {
				console.error('Error fetching follow requests:', error);
			}

		},

		async fetchSharedPosts() {
			try {
				const authToken = localStorage.getItem("userToken");
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}

				console.log("current user ID:" + this.currentUser);
				const response = await axios.get(`${this.HOST_URL}/authors/${this.currentUser}/inbox/`, {
					headers: {
						Authorization: `Token ${authToken}`,
					},
				});

				console.log("Response data:", response.data);

				// Initialize arrays to hold processed posts and likes
				const processedPosts = [];
				const processedLikes = [];

				if (response.data && Array.isArray(response.data.items)) {
					response.data.items.forEach(item => {
						if (item.post) {
							// This item is a shared post
							processedPosts.push({
								id: item.post.id,
								title: item.post.title,
								content: item.post.content,
								shareLink: item.link,
								sender: item.sender,
								senderUsername: item.sender_username,
								published: item.published,
							});
						} else if (item.like) {
							// This item is a like
							processedLikes.push({
								summary: item.like.summary,
								type: item.like.type,
								object: item.like.object,
								sender: item.sender,
								senderUsername: item.sender_username,
								published: item.published,
							});
						}
					});

					// Update component data
					this.sharedPosts = processedPosts;
					this.likes = processedLikes;

				} else {
					console.error("Response data is empty or undefined:", response);
				}

				console.log("Shared posts:", this.sharedPosts);
				console.log("Likes:", this.likes);
			} catch (error) {
				console.error("Error fetching shared posts:", error);
			}
		},
		async deleteAllInboxItems() {
			try {
				const authToken = localStorage.getItem("userToken");
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				console.log("Deleting all inbox items...");
				const response = await axios.delete(`${this.HOST_URL}/authors/${this.currentUser}/inbox/`, {
					headers: {
						Authorization: `Token ${authToken}`,
					},
				});
				// reload the page
				location.reload();
				console.log(response.data);
			} catch (error) {
				console.error("Error deleting inbox items:", error);
			}
		},
		async fetchComments() {
			//console.log("Fetching comments...");
			try {
				const authToken = localStorage.getItem("userToken");
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}

				const response = await axios.get(`${this.HOST_URL}/authors/${this.currentUser}/inbox/`, {
					headers: {
						Authorization: `Token ${authToken}`,
					},
				});

				console.log("Response data for comments:", response.data);

				// Initialize array to hold processed comments
				const processedComments = [];

				if (response.data && Array.isArray(response.data.items)) {
					response.data.items.forEach((item) => {
						if (item.comment) {
							// This item is a comment
							processedComments.push({
								content: item.comment.comment,
								id: item.comment.id,
								postId: item.comment.post_id,
								sender: item.sender,
								senderUsername: item.sender_username,
								published: item.published,
							});
						}
					});

					// Update component data
					this.comments = processedComments;
				} else {
					console.error("Response data is empty or undefined:", response);
				}

				console.log("Comments:", this.comments);
			} catch (error) {
				console.error("Error fetching comments:", error);
			}
		},
	},
};
</script>

<style scoped>
.inbox-container {
	margin: auto;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	padding: 20px;
	border: 1px solid #ccc;
	border-radius: 10px;
}

.section-title {
	font-size: 23px;
	margin-bottom: 10px;
	font-weight: bold;
}

.request-list,
.posts-list {
	list-style: none;
	padding: 0;
}

.request-item {
	display: flex;
	align-items: center;
	justify-content: flex-start;
	/* Change justify-content to flex-start */
	margin-bottom: 10px;
}

.button {
	padding: 5px 15px;
	border-radius: 5px;
	border: none;
	cursor: pointer;
}

.button-space {
	margin-left: 10px;
	/* Adjust the spacing as needed */
}

.accept {
	background-color: #28a745;
	color: white;
}

.deny {
	background-color: #dc3545;
	color: white;
}

.button:hover {
	opacity: 0.8;
}

.profile-photo {
	border-radius: 50%;
	width: 70px;
	height: 70px;
	object-fit: cover;
	border: 2px solid #ddd;
	margin-right: 10px;
}

.profile-info {
	flex-grow: 1;
	/* Allow the profile info to grow and take up remaining space */
}

h3 {
	margin: 0;
	font-size: 1.25rem;
	/* 20px if you're using a 16px base font-size */
	font-weight: bold;
}

.username {
	margin: 0.25rem 0 0;
	/* Only add margin to the top to space it from the display name */
	font-size: 1rem;
	/* 16px if you're using a 16px base font-size */
}

.request-box {
	border: 1px solid #ddd;
	padding: 1rem;
	border-radius: 8px;
	margin: auto;
	max-width: 975px;
	/* Adjust the max width as necessary */
}

.shared-posts {
	margin-top: 10px;
	/* Adjust as needed */
}

.posts-list {
	margin-top: 20px;
	/* Add some space between sections */
}

.post-item,
.like-item,
.comment-item {
	border: 1px solid #ddd;
	padding: 10px;
	margin-bottom: 10px;
	border-radius: 8px;
}

.post-item p,
.like-item p,
.comment-item p {
	margin: 0;
	/* Remove default margins */
	font-weight: bold;
}

.view-post-link,
.view-like-link,
.view-comment-link {
	display: inline-block;
	padding: 5px 10px;
	background-color: #007bff;
	color: #fff;
	text-decoration: none;
	border-radius: 5px;
}

.view-post-link:hover,
.view-like-link:hover,
.view-comment-link:hover {
	background-color: #0056b3;
}

.comment-content {
	margin-top: 10px;
}

/* Added styles for bold text */
.request-item h3,
.request-item .username,
.comment-item p {
	font-weight: bold;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	/* Ensures the title and button are aligned and spaced apart */
}

.delete-inbox-btn {
	padding: 5px 10px;
	background-color: #dc3545;
	color: white;
	border: none;
	border-radius: 5px;
	cursor: pointer;
}

.post-timestamp {
	margin: 0;
	font-size: 0.85em;
	color: #606770;
}


.delete-inbox-btn:hover {
	opacity: 0.8;
}
</style>
