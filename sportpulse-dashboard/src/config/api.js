// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const apiEndpoints = {
  nba: {
    topTeams: `${API_BASE_URL}/api/v1/nba/top-teams`,
    teamMentions: `${API_BASE_URL}/api/v1/nba/team-mentions`,
    teamStats: (teamName) => `${API_BASE_URL}/api/v1/nba/team/${encodeURIComponent(teamName)}`
  },
  football: {
    topTeams: `${API_BASE_URL}/api/v1/football/top-teams`,
    teamMentions: `${API_BASE_URL}/api/v1/football/team-mentions`,
    teamStats: (teamName) => `${API_BASE_URL}/api/v1/football/team/${encodeURIComponent(teamName)}`
  }
};

// Health check endpoint
export const healthCheck = `${API_BASE_URL}/health`;

export default API_BASE_URL;