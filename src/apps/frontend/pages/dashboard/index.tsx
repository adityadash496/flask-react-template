import * as React from 'react';

import { TaskList } from 'frontend/components';

const Dashboard: React.FC = () => (
  <div className="mx-auto max-w-screen-2xl p-4 md:p-6 2xl:p-10">
    <TaskList />
  </div>
);

export default Dashboard;
