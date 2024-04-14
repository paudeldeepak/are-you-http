<template>
	<div class="modal-mask">
		<div class="modal-wrapper">
			<div class="modal-container">
				<div class="modal-header">
					<span class="modal-title">
						<slot name="header">Share Post</slot>
					</span>
					<button class="modal-default-button" @click="$emit('close')">Close</button>
				</div>
				<div class="modal-body">
					<slot name="body"></slot>
					<!-- Share via link section -->
					<div v-if="visibility === 'UNLISTED'" class="share-via-link-section">
						<h4 class="share-via-link">Share Via Link</h4>
						<div class="link-box">
							<input type="text" readonly :value="shareLink" ref="linkInput" />
							<button @click="copyLink">Copy</button>
						</div>
					</div>
					<!-- Share via authors section -->
					<div v-else class="share-via-authors-section">
						<h4 class="share-with-users">Select Users:</h4>
						<div class="authors-list">
							<ul>
								<li v-for="author in paginatedAuthors" :key="author.id">
									<input type="checkbox" v-model="selectedAuthors" :value="author.uid" />
									{{ author.displayName }} <span class="small-host">@{{ author.host }}</span>
								</li>
							</ul>
						</div>
						<!-- Pagination controls -->
						<div class="pagination-controls">
							<button @click="prevPage" :disabled="currentPage <= 1">Previous</button>
							<button @click="nextPage" :disabled="currentPage >= maxPage">Next</button>
						</div>
					</div>
				</div>
				<div class="modal-footer">
					<button v-if="visibility !== 'UNLISTED'" class="modal-default-button"
						@click="emitShareToSelectedAuthors">
						Share To Selected Users
					</button>
					<button v-if="visibility !== 'UNLISTED'" class="modal-default-button" @click="shareToFriends">
						Share To Friends
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import axios from "axios";

export default {
	props: ["authors", "shareLink", "visibility", "postId"],
	data() {
		return {
			HOST_URL: import.meta.env.VITE_HOST_URL,
			selectedAuthors: [],
			currentPage: 1,
			authorsPerPage: 5,
		};
	},
	computed: {
		currentUser() {
			return localStorage.getItem("userId");
		},
		paginatedAuthors() {
			const start = (this.currentPage - 1) * this.authorsPerPage;
			return this.authors.slice(start, start + this.authorsPerPage);
		},
		maxPage() {
			return Math.ceil(this.authors.length / this.authorsPerPage);
		},
	},
	methods: {
		emitShareToSelectedAuthors() {
			this.$emit("sharePost", this.selectedAuthors);
			this.$emit("close");
		},
		nextPage() {
			if (this.currentPage < this.maxPage) this.currentPage++;
		},
		prevPage() {
			if (this.currentPage > 1) this.currentPage--;
		},
		shareToFriends() {
			this.$emit("sharePostFriends");
			this.$emit('close');
		},
	},
};
</script>

<style scoped>

.small-host {
	font-size: 0.7em;
	color: #606770;
}

.modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
}

.modal-wrapper {
	width: 100%;
	max-width: 500px;
}

.modal-container {
	background-color: #fff;
	border: 1px solid #ccc;
	border-radius: 10px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	padding: 20px;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 15px;
}

.modal-header h3 {
	font-size: 2.8rem;
	/* Match the font size with your stream view */
	margin: 10;
	font-weight: bold;
}

.modal-header button {
	background-color: transparent;
	border: none;
	font-size: 1.3em;
	color: #3492c5;
	cursor: pointer;
}

.pagination-controls button {
	margin: 10px 5px;
	padding: 5px 10px;
	background-color: #f0f0f0;
	border: 1px solid #d0d0d0;
	border-radius: 4px;
	cursor: pointer;
}

.pagination-controls button:disabled {
	background-color: #e0e0e0;
	color: #a0a0a0;
	cursor: not-allowed;
}

.modal-header button:hover {
	color: #3087b5;
}

.modal-body {
	margin-bottom: 355px;
}

.modal-body p {
	margin: 0;
	color: #606770;
}

.modal-footer {
	display: flex;
	justify-content: center;

}

.modal-footer button {
	font-size: 1em;
	/* Adjust font size if needed */
	color: #ffffff;
	margin-right: 7px;
	border-radius: 9px;
	padding: 8px 12px;
	/* Updated padding */
	background-color: #3492c5;
	/* Blue color, you can adjust this */
	border: none;
	cursor: pointer;
}

.modal-footer button:hover {
	background-color: #3087b5;
	/* Darker blue color on hover */
}

.modal-footer button:last-child {
	margin-right: 0;
}

.modal-title {
	font-size: 30px;
	font-weight: bold;
	margin: 0;
}

.share-with-users {
	font-size: 1.2em;
	/* Adjust font size */
	font-weight: bold;
	margin-top: 20px;
	/* Add margin to create space between link box and share with users */
}

.share-via-link {
	font-size: 1.2em;
	/* Adjust font size */
	font-weight: bold;
}

.link-box {
	display: flex;
	align-items: center;
	margin-top: 10px;
}

.link-box input {
	flex-grow: 1;
	border: 1px solid #ccc;
	border-radius: 5px;
	padding: 8px;
}

.link-box button {
	margin-left: 10px;
	padding: 8px 12px;
	background-color: #3492c5;
	/* Blue color, you can adjust this */
	color: #ffffff;
	border: none;
	border-radius: 5px;
	cursor: pointer;
}

.link-box button:hover {
	background-color: #3087b5;
	/* Darker blue color on hover */
}
</style>
