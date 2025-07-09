import unittest
import os
import shutil
import json
from core.agent_manager import AgentManager
from datetime import datetime

class TestAgentManager(unittest.TestCase):
    def setUp(self):
        self.test_agents_dir = './agents'
        self.test_logs_dir = './logs'
        os.makedirs(self.test_agents_dir, exist_ok=True)
        os.makedirs(self.test_logs_dir, exist_ok=True)
        self.agent_manager = AgentManager(agents_dir=self.test_agents_dir)

    def tearDown(self):
        shutil.rmtree(self.test_agents_dir, ignore_errors=True)
        shutil.rmtree(self.test_logs_dir, ignore_errors=True)

    def _create_log_file(self, conversation_id, success=True):
        log_file = os.path.join(self.test_logs_dir, f'{conversation_id}.jsonl')
        interaction = {
            'type': 'interaction',
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'input': 'test input',
            'response': {'result': 'test'}
        }
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(interaction) + '\n')
        return log_file

    def test_save_agent_success(self):
        conversation_id = 'agent_20250709_121240_556a7927'
        self._create_log_file(conversation_id)
        # Patch log path in AgentManager
        orig_logs = 'logs'
        os.rename(self.test_logs_dir, orig_logs)
        try:
            result = self.agent_manager.save_agent('test_agent', conversation_id)
            self.assertTrue(result)
            agent_folder = os.path.join(self.test_agents_dir, 'test_agent')
            self.assertTrue(os.path.exists(os.path.join(agent_folder, 'main_agent.jsonl')))
            self.assertTrue(os.path.exists(os.path.join(agent_folder, 'metadata.json')))
        finally:
            os.rename(orig_logs, self.test_logs_dir)

    def test_save_agent_no_log(self):
        result = self.agent_manager.save_agent('test_agent2', 'nonexistent_convo')
        self.assertFalse(result)

    def test_list_agents(self):
        conversation_id = 'test_convo_2'
        self._create_log_file(conversation_id)
        orig_logs = 'logs'
        os.rename(self.test_logs_dir, orig_logs)
        try:
            self.agent_manager.save_agent('test_agent3', conversation_id)
            agents = self.agent_manager.list_agents()
            self.assertEqual(len(agents), 1)
            self.assertEqual(agents[0]['agent_name'], 'test_agent3')
        finally:
            os.rename(orig_logs, self.test_logs_dir)

    def test_get_agent_path(self):
        conversation_id = 'test_convo_3'
        self._create_log_file(conversation_id)
        orig_logs = 'logs'
        os.rename(self.test_logs_dir, orig_logs)
        try:
            self.agent_manager.save_agent('test_agent4', conversation_id)
            path = self.agent_manager.get_agent_path('test_agent4')
            self.assertTrue(os.path.exists(path))
        finally:
            os.rename(orig_logs, self.test_logs_dir)

if __name__ == '__main__':
    unittest.main()
