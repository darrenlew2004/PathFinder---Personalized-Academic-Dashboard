import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  School,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { AppDispatch, RootState } from '../../store';
import { fetchStudentStats } from '../../features/studentSlice';

const RISK_COLORS = {
  LOW: '#4caf50',
  MEDIUM: '#ff9800',
  HIGH: '#f44336',
};

const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { stats, loading, error } = useSelector((state: RootState) => state.students);
  const { user } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    dispatch(fetchStudentStats());
  }, [dispatch]);

  if (loading && !stats) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!stats) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">No student data available</Alert>
      </Container>
    );
  }

  const riskDistributionData = Object.entries(stats.riskDistribution).map(([name, value]) => ({
    name,
    value,
    color: RISK_COLORS[name as keyof typeof RISK_COLORS],
  }));

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Welcome back, {user?.name}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's an overview of your academic progress
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Current GPA
                  </Typography>
                  <Typography variant="h4">{stats.student.gpa.toFixed(2)}</Typography>
                </Box>
                <TrendingUp color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Completed Courses
                  </Typography>
                  <Typography variant="h4">{stats.completedCourses}</Typography>
                </Box>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Total Credits
                  </Typography>
                  <Typography variant="h4">{stats.totalCredits}</Typography>
                </Box>
                <School color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Avg Attendance
                  </Typography>
                  <Typography variant="h4">
                    {(stats.averageAttendance * 100).toFixed(0)}%
                  </Typography>
                </Box>
                <Warning color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Current Courses */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Courses
              </Typography>
              {stats.currentCourses.length === 0 ? (
                <Alert severity="info">No enrolled courses</Alert>
              ) : (
                <Box mt={2}>
                  {stats.currentCourses.map((courseProgress) => (
                    <Box key={courseProgress.course.id} mb={3}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {courseProgress.course.courseCode} - {courseProgress.course.courseName}
                        </Typography>
                        {courseProgress.riskPrediction && (
                          <Chip
                            label={courseProgress.riskPrediction.riskLevel}
                            size="small"
                            sx={{
                              bgcolor: RISK_COLORS[courseProgress.riskPrediction.riskLevel],
                              color: 'white',
                            }}
                          />
                        )}
                      </Box>

                      <Box mb={1}>
                        <Box display="flex" justifyContent="space-between" mb={0.5}>
                          <Typography variant="body2" color="text.secondary">
                            Attendance: {(courseProgress.enrollment.attendanceRate * 100).toFixed(0)}%
                          </Typography>
                          {courseProgress.riskPrediction && (
                            <Typography variant="body2" color="text.secondary">
                              Predicted Grade: {courseProgress.riskPrediction.predictedGrade || 'N/A'}
                            </Typography>
                          )}
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={courseProgress.enrollment.attendanceRate * 100}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>

                      {courseProgress.riskPrediction && courseProgress.riskPrediction.recommendations.length > 0 && (
                        <Box mt={1}>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            Recommendations:
                          </Typography>
                          <ul style={{ margin: 0, paddingLeft: 20 }}>
                            {courseProgress.riskPrediction.recommendations.slice(0, 2).map((rec, idx) => (
                              <li key={idx}>
                                <Typography variant="body2">{rec}</Typography>
                              </li>
                            ))}
                          </ul>
                        </Box>
                      )}
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Distribution
              </Typography>
              {riskDistributionData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={riskDistributionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {riskDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Alert severity="info">No risk data available</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;