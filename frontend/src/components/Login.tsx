import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Tab,
  Tabs,
  CircularProgress,
} from '@mui/material';
import { School } from '@mui/icons-material';
import { AppDispatch, RootState } from '../../store';
import { login, clearError } from '../../features/authSlice';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const Login: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { loading, error, isAuthenticated } = useSelector((state: RootState) => state.auth);

  const [tabValue, setTabValue] = useState(0);
  const [loginData, setLoginData] = useState({ student_id: '' });

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  React.useEffect(() => {
    dispatch(clearError());
  }, [tabValue, dispatch]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const studentId = parseInt(loginData.student_id);
    if (isNaN(studentId)) {
      return;
    }
    await dispatch(login({ student_id: studentId }));
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Card elevation={8}>
          <CardContent sx={{ p: 4 }}>
            <Box display="flex" flexDirection="column" alignItems="center" mb={3}>
              <School sx={{ fontSize: 60, color: '#667eea', mb: 2 }} />
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Student Risk Prediction
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Manage your academic journey with data-driven insights
              </Typography>
            </Box>

            <Tabs value={tabValue} onChange={handleTabChange} centered sx={{ mb: 2 }}>
              <Tab label="Login" />
              <Tab label="Register" disabled />
            </Tabs>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <TabPanel value={tabValue} index={0}>
              <form onSubmit={handleLoginSubmit}>
                <TextField
                  fullWidth
                  label="Student ID"
                  type="number"
                  value={loginData.student_id}
                  onChange={(e) => setLoginData({ ...loginData, student_id: e.target.value })}
                  required
                  sx={{ mb: 3 }}
                  helperText="Enter your numeric student ID to login"
                />
                <Button
                  fullWidth
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                    },
                  }}
                >
                  {loading ? <CircularProgress size={24} color="inherit" /> : 'Login'}
                </Button>
              </form>
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <Alert severity="info" sx={{ mb: 2 }}>
                Registration is currently disabled. Please contact your administrator to get access.
              </Alert>
            </TabPanel>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Login;