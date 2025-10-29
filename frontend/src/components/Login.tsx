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
import { login, register, clearError } from '../../features/authSlice';

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
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [registerData, setRegisterData] = useState({
    studentId: '',
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    gpa: '',
    semester: '',
  });

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
    await dispatch(login(loginData));
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (registerData.password !== registerData.confirmPassword) {
      return;
    }

    const userData = {
      studentId: registerData.studentId,
      name: registerData.name,
      email: registerData.email,
      password: registerData.password,
      gpa: registerData.gpa ? parseFloat(registerData.gpa) : undefined,
      semester: registerData.semester ? parseInt(registerData.semester) : undefined,
    };

    await dispatch(register(userData));
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
              <Tab label="Register" />
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
                  label="Email"
                  type="email"
                  value={loginData.email}
                  onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                  required
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Password"
                  type="password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                  required
                  sx={{ mb: 3 }}
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
              <form onSubmit={handleRegisterSubmit}>
                <TextField
                  fullWidth
                  label="Student ID"
                  value={registerData.studentId}
                  onChange={(e) => setRegisterData({ ...registerData, studentId: e.target.value })}
                  required
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Full Name"
                  value={registerData.name}
                  onChange={(e) => setRegisterData({ ...registerData, name: e.target.value })}
                  required
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={registerData.email}
                  onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                  required
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Password"
                  type="password"
                  value={registerData.password}
                  onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                  required
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Confirm Password"
                  type="password"
                  value={registerData.confirmPassword}
                  onChange={(e) => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
                  required
                  error={registerData.password !== registerData.confirmPassword && registerData.confirmPassword !== ''}
                  helperText={
                    registerData.password !== registerData.confirmPassword && registerData.confirmPassword !== ''
                      ? 'Passwords do not match'
                      : ''
                  }
                  sx={{ mb: 2 }}
                />
                <Box display="flex" gap={2} mb={3}>
                  <TextField
                    fullWidth
                    label="Current GPA"
                    type="number"
                    inputProps={{ step: '0.01', min: '0', max: '4' }}
                    value={registerData.gpa}
                    onChange={(e) => setRegisterData({ ...registerData, gpa: e.target.value })}
                  />
                  <TextField
                    fullWidth
                    label="Semester"
                    type="number"
                    inputProps={{ min: '1', max: '12' }}
                    value={registerData.semester}
                    onChange={(e) => setRegisterData({ ...registerData, semester: e.target.value })}
                  />
                </Box>
                <Button
                  fullWidth
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading || registerData.password !== registerData.confirmPassword}
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                    },
                  }}
                >
                  {loading ? <CircularProgress size={24} color="inherit" /> : 'Register'}
                </Button>
              </form>
            </TabPanel>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Login;