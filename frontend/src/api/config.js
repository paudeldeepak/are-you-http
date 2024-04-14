const APIURLS = {
    "development": "http://localhost:8000",
    "production": "https://are-you-http-1-8cbfdddfbe37.herokuapp.com",
};



export const getAuthorizationHeader = () => {
    return `Token ${localStorage.getItem('user_token') || ''}`;
};

export const getAuthorId = () => localStorage.getItem('user_id') || '';
export const APIURL = APIURLS[process.env.NODE_ENV || "development"];
export const REFRESH_INTERVAL = 3000;
